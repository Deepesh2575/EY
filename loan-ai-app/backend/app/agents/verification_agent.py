import asyncio
import logging
from typing import Dict, Any
from app.services.claude_service import ClaudeService

logger = logging.getLogger(__name__)

import re

class VerificationAgent:
    """Handles KYC and document verification"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.pan_regex = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")

    async def verify_documents(
        self,
        documents: Dict[str, str],
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate document verification
        
        Args:
            documents: Dictionary of doc_type -> file_path or filename
            user_data: User application data
        
        Returns:
            {
                "passed": bool,
                "missing_docs": List[str],
                "message": str
            }
        """
        required_docs = ["salary_slip", "pan_card", "video_kyc_selfie"]
        missing = [doc for doc in required_docs if doc not in documents]

        if missing:
            doc_names = {
                "salary_slip": "Salary Slip",
                "pan_card": "PAN Card",
                "aadhaar": "Aadhaar Card",
                "bank_statement": "Bank Statement",
                "video_kyc_selfie": "Video KYC Selfie"
            }
            
            missing_names = [doc_names.get(doc, doc) for doc in missing]
            
            return {
                "passed": False,
                "missing_docs": missing,
                "message": f"Please upload: {', '.join(missing_names)}"
            }

        # Validate PAN card format
        pan_card_filename = documents.get("pan_card")
        if pan_card_filename and not self.pan_regex.match(pan_card_filename):
            return {
                "passed": False,
                "message": "Invalid PAN card format."
            }

        # Simulate verification delay
        await asyncio.sleep(1)
        
        # In production, this would:
        # 1. Extract text from PDF/images using OCR
        # 2. Validate document format
        # 3. Cross-check information with user_data
        # 4. Use Claude Vision API to verify document authenticity
        
        return {
            "passed": True,
            "message": "All documents verified successfully",
            "verified_docs": list(documents.keys())
        }
    
    async def process_document(
        self, 
        file_info: dict, 
        file_content: bytes, 
        conversation_id: str
    ) -> dict:
        """Process an uploaded document"""
        # In a real implementation, this would:
        # 1. Save file to storage (S3, local filesystem)
        # 2. Extract text from PDF/images using OCR (Tesseract, AWS Textract)
        # 3. Validate document format
        # 4. Extract relevant information (salary, PAN number, etc.)
        # 5. Store document securely
        
        # For MVP, just acknowledge receipt
        await asyncio.sleep(0.5)  # Simulate processing
        
        return {
            "status": "received",
            "filename": file_info.get("filename"),
            "message": "Document received and is being processed. We'll verify the information shortly."
        }
    
    async def handle_message(self, message: str, conversation_id: str) -> str:
        """Legacy method for backward compatibility"""
        system_prompt = """You are a KYC (Know Your Customer) verification agent. Your role is to:
        1. Guide customers through the verification process
        2. Request necessary documents (ID, proof of address, income statements)
        3. Explain verification requirements
        4. Confirm when documents are received and being processed
        
        Be clear about what documents are needed and why. Maintain a professional, reassuring tone."""
        
        prompt = f"""{system_prompt}

        User Message: {message}
        
        Provide a helpful response about the verification process.
        """
        
        response = await self.claude_service.get_completion(prompt)
        return response
