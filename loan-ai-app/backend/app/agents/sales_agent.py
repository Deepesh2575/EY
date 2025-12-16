import json
import logging
from typing import List, Dict, Any
from app.models import Message
from app.services.claude_service import ClaudeService
from app.services.mock_data import get_loan_products

logger = logging.getLogger(__name__)

class SalesAgent:
    """Handles persuasive, human-like sales conversation"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.loan_products = get_loan_products()
    
    async def greet_and_initiate(self, user_message: str, messages: List[Message]) -> str:
        """Warm, persuasive greeting"""
        system_prompt = """You are a friendly, persuasive loan sales executive for an NBFC (similar to Tata Capital style).

Your goal:
- Build trust quickly
- Make the customer feel valued
- Guide them smoothly toward applying
- Be conversational, not robotic
- Show enthusiasm and professionalism

Start with a warm greeting and ask how you can help them today. Be natural and engaging."""
        
        # Build conversation context
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-5:]  # Last 5 messages for context
        ]
        
        # If no previous messages, start fresh
        if not conversation_messages:
            conversation_messages = [{"role": "user", "content": user_message}]
        
        response = await self.claude_service.chat(
            system_prompt=system_prompt,
            messages=conversation_messages,
            max_tokens=200
        )
        
        return response
    
    async def ask_missing_info(self, current_data: Dict[str, Any], messages: List[Message]) -> str:
        """Intelligently ask for missing information"""
        # Determine what's missing
        missing_fields = []
        field_priority = ["loan_amount", "loan_purpose", "monthly_salary", "employment_type", "name"]
        
        for field in field_priority:
            if not current_data.get(field):
                missing_fields.append(field)
                break  # Ask for one at a time
        
        if not missing_fields:
            # All info collected, but double-check
            return await self.confirm_details(current_data, messages)
        
        field_name = missing_fields[0]
        field_descriptions = {
            "loan_amount": "the loan amount you need",
            "loan_purpose": "the purpose of the loan (e.g., home renovation, medical expenses, education)",
            "monthly_salary": "your monthly salary or income",
            "employment_type": "your employment type (salaried, self-employed, business owner)",
            "name": "your full name"
        }
        
        system_prompt = f"""You are a friendly loan sales executive. The customer is applying for a loan.

Current information collected:
{json.dumps(current_data, indent=2)}

You need to ask for: {field_descriptions.get(field_name, field_name)}

Ask for this information in a natural, conversational way. Explain WHY you need this info (e.g., "to determine your eligibility").
Be friendly and make it feel like a conversation, not an interrogation."""
        
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-5:]
        ]
        
        response = await self.claude_service.chat(
            system_prompt=system_prompt,
            messages=conversation_messages,
            max_tokens=150
        )
        
        return response
    
    async def confirm_details(self, loan_data: Dict[str, Any], messages: List[Message]) -> str:
        """Confirm all details before proceeding"""
        system_prompt = """You are a loan sales executive confirming loan application details.

Summarize all the collected information clearly and ask the customer to confirm if everything is correct.
Be friendly and professional. Once confirmed, let them know the next steps (document verification)."""
        
        summary = f"""
Loan Application Summary:
- Name: {loan_data.get('name', 'Not provided')}
- Loan Amount: ₹{loan_data.get('loan_amount', 0):,.0f}
- Loan Purpose: {loan_data.get('loan_purpose', 'Not provided')}
- Monthly Salary: ₹{loan_data.get('monthly_salary', 0):,.0f}
- Employment Type: {loan_data.get('employment_type', 'Not provided')}
"""
        
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-3:]
        ]
        conversation_messages.append({
            "role": "user",
            "content": f"Please confirm these details: {summary}"
        })
        
        response = await self.claude_service.chat(
            system_prompt=system_prompt,
            messages=conversation_messages,
            max_tokens=200
        )
        
        return response
    
    async def handle_message(self, message: str, conversation_id: str) -> str:
        """Legacy method for backward compatibility"""
        system_prompt = """You are a professional loan sales agent. Your role is to:
        1. Provide information about loan products
        2. Answer questions about interest rates, terms, and eligibility
        3. Guide customers through the initial loan inquiry process
        4. Collect basic information needed to proceed
        
        Be friendly, professional, and helpful. Always provide accurate information."""
        
        products_info = "\n".join([
            f"- {product['name']}: {product['description']} (Rate: {product['rate']}%, Max Amount: ₹{product['max_amount']:,})"
            for product in self.loan_products
        ])
        
        enhanced_prompt = f"""{system_prompt}

        Available Loan Products:
        {products_info}

        User Message: {message}
        
        Provide a helpful response to the user's inquiry.
        """
        
        response = await self.claude_service.get_completion(enhanced_prompt)
        return response
