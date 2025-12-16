import os
import logging
from datetime import datetime
from typing import Dict, Any
from app.services.claude_service import ClaudeService
from app.utils.helpers import generate_sanction_letter

logger = logging.getLogger(__name__)

class SanctionAgent:
    """Handles final loan sanction and document generation"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        # Create directory for generated documents
        self.doc_dir = "./generated_docs"
        os.makedirs(self.doc_dir, exist_ok=True)
    
    async def generate_letter(self, user_data: Dict[str, Any]) -> str:
        """
        Generate professional sanction letter PDF
        
        Args:
            user_data: Dictionary containing loan details
        
        Returns:
            File path to generated PDF
        """
        try:
            # Generate PDF using helper function
            pdf_bytes = generate_sanction_letter(user_data)
            
            # Save to file
            name = user_data.get("name", "Customer").replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sanction_letter_{name}_{timestamp}.pdf"
            filepath = os.path.join(self.doc_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
            
            logger.info(f"Generated sanction letter: {filepath}")
            
            # Return relative path (in production, return S3 URL or signed URL)
            return filepath
        
        except Exception as e:
            logger.error(f"Error generating sanction letter: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate sanction letter: {str(e)}")
    
    async def handle_message(self, message: str, conversation_id: str) -> str:
        """Legacy method for backward compatibility"""
        system_prompt = """You are a loan sanction agent. Your role is to:
        1. Provide final loan approval information
        2. Explain loan terms and conditions
        3. Guide customers on next steps after approval
        4. Assist with sanction letter generation
        
        Be clear and celebratory (when appropriate) while maintaining professionalism."""
        
        prompt = f"""{system_prompt}

        User Message: {message}
        
        Provide a helpful response about the loan sanction process.
        """
        
        response = await self.claude_service.get_completion(prompt)
        return response
