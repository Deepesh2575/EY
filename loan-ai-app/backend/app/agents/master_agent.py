import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.claude_service import ClaudeService
from app.agents.sales_agent import SalesAgent
from app.agents.verification_agent import VerificationAgent
from app.agents.underwriting_agent import UnderwritingAgent
from app.agents.sanction_agent import SanctionAgent
from app.models import ConversationState, Message, LoanApplication

logger = logging.getLogger(__name__)

class MasterAgent:
    """Intelligent orchestrator that manages conversation flow and delegates to worker agents"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.sanction_agent = SanctionAgent()
        
        # In-memory conversation storage (replace with Redis/DB in production)
        self.conversations: Dict[str, ConversationState] = {}
    
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = ConversationState(
            conversation_id=conversation_id,
            stage="GREETING",
            messages=[],
            loan_application=LoanApplication(),
            documents={},
            decision=None
        )
        return conversation_id
    
    def get_conversation_state(self, conversation_id: str) -> Optional[ConversationState]:
        """Get conversation state"""
        return self.conversations.get(conversation_id)
    
    async def process_message(
        self, 
        conversation_state: ConversationState, 
        user_message: str
    ) -> Dict[str, Any]:
        """
        Main orchestration logic that routes messages based on conversation stage
        
        Returns:
            {
                "response": str,
                "next_stage": str,
                "conversation_state": ConversationState
            }
        """
        # Add user message to history
        conversation_state.messages.append(
            Message(role="user", content=user_message, timestamp=datetime.now())
        )
        
        current_stage = conversation_state.stage
        response = ""
        next_stage = current_stage
        sanction_letter_path = None
        
        try:
            if current_stage == "GREETING":
                response = await self.sales_agent.greet_and_initiate(
                    user_message, 
                    conversation_state.messages
                )
                next_stage = "INFO_GATHERING"
            
            elif current_stage == "INFO_GATHERING":
                # Extract loan information from conversation
                loan_data = await self._extract_loan_info(conversation_state.messages)
                
                # Update loan_application with extracted information
                if loan_data:
                    conversation_state.loan_application = loan_data
                
                # Check if we have all required information
                if self._is_info_complete(conversation_state.loan_application):
                    response = await self.sales_agent.confirm_details(
                        conversation_state.loan_application.dict(),
                        conversation_state.messages
                    )
                    next_stage = "VERIFICATION"
                else:
                    response = await self.sales_agent.ask_missing_info(
                        conversation_state.loan_application.dict(),
                        conversation_state.messages
                    )
                    next_stage = "INFO_GATHERING"
            
            elif current_stage == "VERIFICATION":
                # Check documents and KYC
                verification_result = await self.verification_agent.verify_documents(
                    conversation_state.documents,
                    conversation_state.loan_application.dict()
                )
                
                if verification_result["passed"]:
                    response = "Great! Your documents are verified. Now analyzing your eligibility..."
                    next_stage = "UNDERWRITING"
                else:
                    missing_docs = verification_result.get("missing_docs", [])
                    
                    if "video_kyc_selfie" in missing_docs:
                        response = "We need to verify your identity. Please complete the Video KYC process by taking a selfie."
                        next_stage = "VIDEO_KYC"
                    else:
                        response = f"We need the following documents: {', '.join(missing_docs)}. Please upload them to proceed."
                        next_stage = "VERIFICATION"

            elif current_stage == "VIDEO_KYC":
                 # Check if video kyc is now present
                if "video_kyc_selfie" in conversation_state.documents:
                     response = "✅ Video KYC received and verified! Proceeding with final checks."
                     # Re-run verification to ensure everything else is also there
                     verification_result = await self.verification_agent.verify_documents(
                        conversation_state.documents,
                        conversation_state.loan_application.dict()
                    )
                     if verification_result["passed"]:
                        next_stage = "UNDERWRITING"
                     else:
                        missing_docs = verification_result.get("missing_docs", [])
                        response += f"\n\nWe still need: {', '.join(missing_docs)}."
                        next_stage = "VERIFICATION"
                else:
                     response = "Please complete the Video KYC to proceed."
                     next_stage = "VIDEO_KYC"
            
            elif current_stage == "UNDERWRITING":
                # Risk assessment
                decision = await self.underwriting_agent.assess_risk(
                    conversation_state.loan_application.dict()
                )
                
                conversation_state.decision = decision["status"]
                
                if decision["status"] == "APPROVED":
                    loan_amount = conversation_state.loan_application.loan_amount or 0
                    response = f"🎉 Congratulations! Your loan of ₹{loan_amount:,.0f} is APPROVED!"
                    response += f"\n\nApproved Amount: ₹{decision.get('approved_amount', loan_amount):,.0f}"
                    response += f"\nInterest Rate: {decision.get('interest_rate', 12.5)}% per annum"
                    response += f"\nTenure: {decision.get('tenure', 36)} months"
                    response += f"\nMonthly EMI: ₹{decision.get('monthly_emi', 0):,.0f}"
                    next_stage = "SANCTION"
                else:
                    reason = decision.get("reason", "Eligibility criteria not met")
                    response = f"Sorry, we cannot approve your loan at this time.\n\nReason: {reason}"
                    if decision.get("suggestions"):
                        response += f"\n\nSuggestions: {decision.get('suggestions')}"
                    next_stage = "COMPLETED"
            
            elif current_stage == "SANCTION":
                # Generate PDF sanction letter
                pdf_path = await self.sanction_agent.generate_letter(
                    conversation_state.loan_application.dict()
                )
                sanction_letter_path = pdf_path
                response = "Your sanction letter has been generated successfully!\n\n"
                response += f"You can download it from: {pdf_path}\n\n"
                response += "Please review the terms and conditions. Our team will contact you shortly to proceed with disbursement."
                next_stage = "COMPLETED"
            
            else:
                # Default fallback
                response = "Thank you for your interest. How can I assist you today?"
                next_stage = "GREETING"
        
        except Exception as e:
            logger.error(f"Error in MasterAgent.process_message: {str(e)}", exc_info=True)
            response = "I apologize, but I encountered an error processing your request. Please try again."
            next_stage = current_stage
        
        # Update conversation state
        conversation_state.stage = next_stage
        
        # Add assistant response to history
        conversation_state.messages.append(
            Message(role="assistant", content=response, timestamp=datetime.now())
        )
        
        return {
            "response": response,
            "next_stage": next_stage,
            "conversation_state": conversation_state,
            "sanction_letter_path": sanction_letter_path
        }
    
    async def _extract_loan_info(self, messages: List[Message]) -> Optional[LoanApplication]:
        """Extract structured loan information from conversation history"""
        # Build conversation context
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in messages[-10:]  # Last 10 messages
        ])
        
        schema = {
            "name": "Full name of the applicant",
            "loan_amount": "Loan amount requested (number only)",
            "loan_purpose": "Purpose of the loan",
            "monthly_salary": "Monthly salary/income (number only)",
            "employment_type": "Type of employment (salaried, self-employed, etc.)",
            "pan_number": "PAN card number if mentioned"
        }
        
        try:
            extracted = await self.claude_service.extract_structured_data(
                conversation_text,
                schema
            )
            
            # Convert string numbers to floats
            if "loan_amount" in extracted and extracted["loan_amount"]:
                try:
                    val = str(extracted["loan_amount"]).replace(',', '').replace('_', '').strip()
                    extracted["loan_amount"] = float(val)
                except (ValueError, TypeError):
                    extracted["loan_amount"] = 0
            
            if "monthly_salary" in extracted and extracted["monthly_salary"]:
                try:
                    val = str(extracted["monthly_salary"]).replace(',', '').replace('_', '').strip()
                    extracted["monthly_salary"] = float(val)
                except (ValueError, TypeError):
                    extracted["monthly_salary"] = 0
            
            return LoanApplication(**extracted)
        except ValueError as e:
            logger.error(f"Could not extract loan info from conversation: {e}")
            return None
    
    def _is_info_complete(self, loan_application: LoanApplication) -> bool:
        """Check if all required information is collected"""
        if not loan_application:
            return False

        required_fields = ["name", "loan_amount", "loan_purpose", "monthly_salary", "employment_type"]
        
        for field in required_fields:
            if not getattr(loan_application, field):
                return False
        
        # Validate that numeric fields are positive
        if loan_application.loan_amount <= 0:
            return False
        if loan_application.monthly_salary <= 0:
            return False
        
        return True
    
    async def process_file(
        self, 
        conversation_state: ConversationState,
        file_info: Dict[str, Any], 
        file_content: bytes, 
        doc_type: str = "salary_slip"
    ) -> Dict[str, Any]:
        """Process an uploaded file"""
        # Store document (in production, save to S3 or file system)
        # For now, just mark as uploaded
        conversation_state.documents[doc_type] = file_info.get("filename", "uploaded_file")
        
        # Process through verification agent
        try:
            result = await self.verification_agent.process_document(
                file_info, 
                file_content, 
                conversation_state.conversation_id
            )
            return {
                "message": result.get("message", "File processed successfully"),
                "conversation_id": conversation_state.conversation_id,
                "file_info": file_info,
                "doc_type": doc_type
            }
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {
                "message": f"Error processing file: {str(e)}",
                "conversation_id": conversation_state.conversation_id,
                "file_info": file_info
            }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history as list of dicts"""
        if conversation_id not in self.conversations:
            return []
        
        state = self.conversations[conversation_id]
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in state.messages
        ]
