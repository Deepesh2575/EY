import logging
from typing import Dict, Any
from app.services.claude_service import ClaudeService
from app.services.mock_data import MockDataService

logger = logging.getLogger(__name__)

class UnderwritingAgent:
    """Handles credit assessment and underwriting decisions"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.mock_service = MockDataService()
    
    async def assess_risk(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loan approval logic with eligibility rules
        
        Rules:
        1. Salary >= 3x monthly EMI
        2. Loan amount <= 10x monthly salary
        3. No existing loan > 50% of salary
        4. Credit score > 650 (if available)
        
        Returns:
            {
                "status": "APPROVED" | "REJECTED" | "MANUAL_REVIEW",
                "reason": str,
                "approved_amount": float,
                "interest_rate": float,
                "tenure": int,
                "monthly_emi": float,
                "suggestions": List[str]
            }
        """
        loan_amount = user_data.get("loan_amount", 0)
        monthly_salary = user_data.get("monthly_salary", 0)
        pan_number = user_data.get("pan_number")
        
        # Get credit score (mock for now)
        credit_score = user_data.get("credit_score")
        if not credit_score and pan_number:
            credit_score = await self.mock_service.get_credit_score(pan_number)
            user_data["credit_score"] = credit_score
        
        # Get existing loans
        existing_loans_info = {}
        if pan_number:
            existing_loans_info = await self.mock_service.check_existing_loans(pan_number)
            user_data["existing_loans"] = existing_loans_info.get("existing_loans", 0)
            user_data["outstanding_emi"] = existing_loans_info.get("outstanding_emi", 0)
        
        existing_loans = user_data.get("existing_loans", 0)
        
        # Calculate EMI (assuming 12.5% interest, 36 months tenure)
        interest_rate = 12.5
        tenure_months = 36
        monthly_interest = interest_rate / 12 / 100
        monthly_emi = (loan_amount * monthly_interest * (1 + monthly_interest) ** tenure_months) / \
                      ((1 + monthly_interest) ** tenure_months - 1)
        
        # Rule 1: Salary >= 3x monthly EMI
        if monthly_salary < monthly_emi * 3:
            return {
                "status": "REJECTED",
                "reason": f"Monthly salary (₹{monthly_salary:,.0f}) is insufficient for EMI repayment (₹{monthly_emi:,.0f}). Required: ₹{monthly_emi * 3:,.0f}",
                "suggestions": [
                    "Consider reducing the loan amount",
                    "Increase the loan tenure",
                    "Wait until your salary increases"
                ]
            }
        
        # Rule 2: Loan amount <= 10x monthly salary
        max_eligible = monthly_salary * 10
        if loan_amount > max_eligible:
            return {
                "status": "REJECTED",
                "reason": f"Loan amount (₹{loan_amount:,.0f}) exceeds eligibility limit (₹{max_eligible:,.0f}). Maximum eligible: 10x monthly salary",
                "suggestions": [
                    f"Reduce loan amount to ₹{max_eligible:,.0f} or less",
                    "Consider applying after salary increase"
                ]
            }
        
        # Rule 3: Existing loans <= 50% of salary
        if existing_loans > monthly_salary * 0.5:
            return {
                "status": "REJECTED",
                "reason": f"Existing loans (₹{existing_loans:,.0f}) exceed 50% of monthly salary. This indicates high debt burden.",
                "suggestions": [
                    "Pay off existing loans first",
                    "Reduce the new loan amount"
                ]
            }
        
        # Rule 4: Credit score check
        if credit_score and credit_score < 650:
            return {
                "status": "REJECTED",
                "reason": f"Credit score ({credit_score}) is below minimum requirement (650)",
                "suggestions": [
                    "Improve your credit score by paying bills on time",
                    "Reduce existing debt",
                    "Wait 3-6 months and reapply"
                ]
            }
        
        # All rules passed - APPROVED
        return {
            "status": "APPROVED",
            "reason": "All eligibility criteria met",
            "approved_amount": loan_amount,
            "interest_rate": interest_rate,
            "tenure": tenure_months,
            "monthly_emi": monthly_emi,
            "credit_score": credit_score,
            "suggestions": []
        }
    
    async def handle_message(self, message: str, conversation_id: str) -> str:
        """Legacy method for backward compatibility"""
        system_prompt = """You are an underwriting agent. Your role is to:
        1. Assess creditworthiness based on provided information
        2. Explain underwriting criteria and decisions
        3. Provide risk assessments
        4. Guide customers on improving their loan eligibility
        
        Be professional and transparent about the assessment process. Explain decisions clearly."""
        
        prompt = f"""{system_prompt}

        User Message: {message}
        
        Provide a helpful response about the underwriting process.
        """
        
        response = await self.claude_service.get_completion(prompt)
        return response
