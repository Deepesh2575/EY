import os
import json
import logging
from typing import List, Dict, Any

try:
    from anthropic import AsyncAnthropic
except Exception:
    AsyncAnthropic = None

from httpx import HTTPStatusError

logger = logging.getLogger(__name__)


import time

class ClaudeService:
    """Service for interacting with Claude API.

    If `ANTHROPIC_API_KEY` is missing or invalid, the service falls back to a
    lightweight mock responder so the app remains usable during local development.
    """

    def __init__(self, retries: int = 2, delay: int = 5):
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.use_mock = False
        self.retries = retries
        self.delay = delay

        if not api_key or AsyncAnthropic is None:
            logger.warning("Anthropic client unavailable or ANTHROPIC_API_KEY not set — using mock LLM.")
            self.client = None
            self.use_mock = True
        else:
            try:
                self.client = AsyncAnthropic(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.client = None
                self.use_mock = True

    async def chat(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000
    ) -> str:
        """
        Send request to Claude API with conversation history
        
        Args:
            system_prompt: System prompt defining agent behavior
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens in response
        
        Returns:
            Response text from Claude
        """
        if self.use_mock:
            return self._mock_response(messages)

        for attempt in range(self.retries):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages
                )

                if response.content and len(response.content) > 0:
                    return response.content[0].text
                else:
                    logger.warning("Empty response from Claude API")
                    return "I apologize, but I couldn't generate a response."

            except HTTPStatusError as he:
                status_code = he.response.status_code
                logger.error(f"Claude API HTTP error on attempt {attempt + 1}: {status_code} - {he}")
                if status_code == 401:
                    logger.error("Anthropic API key appears invalid (401). Switching to mock responder.")
                    self.use_mock = True
                    return self._mock_response(messages)
                if status_code >= 500 and attempt < self.retries - 1:
                    time.sleep(self.delay)
                    continue
                return "I apologize, but I'm experiencing technical difficulties. Please try again later."

            except Exception as e:
                logger.error(f"Claude API error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.retries - 1:
                    time.sleep(self.delay)
                    continue
                self.use_mock = True
                return self._mock_response(messages)
        return "I apologize, but I'm experiencing technical difficulties after multiple retries. Please try again later."

    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a mock response for local development."""
        txt = "I apologize, but I'm experiencing technical difficulties. Please try again later."
        lc = " ".join([m.get('content','').lower() for m in messages])
        if 'what document' in lc or 'documents' in lc or 'document required' in lc:
            return (
                "For loan processing we typically need: PAN card, government ID (passport/driver's license), "
                "recent salary slips (3 months) or bank statements, and address proof. Please upload the files."
            )
        if 'hello' in lc or 'hi' in lc or 'welcome' in lc:
            return "Hello! How can I help you with your loan application today?"
        return txt

    async def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from conversation using Claude
        
        Args:
            text: User input text
            schema: Dictionary describing what data to extract
        
        Returns:
            Extracted data as dictionary
        
        Raises:
            ValueError: If the response from Claude is not valid JSON.
        """

        # Handle mock mode directly for structured data
        if self.use_mock:
            logger.info("Extracting structured data in mock mode")
            mock_data = {}
            text_lower = text.lower()
            
            # Simple heuristic extraction for mock mode
            import re
            
            # Extract numbers for amount/salary
            numbers = re.findall(r'[\d,]+', text)
            numbers = [float(n.replace(',', '')) for n in numbers if n.replace(',', '').isdigit()]
            
            if numbers:
                # Guess: larger number is loan amount, smaller is salary (very rough heuristic)
                numbers.sort(reverse=True)
                if "loan" in text_lower and "amount" in text_lower:
                    if "loan_amount" in schema:
                        mock_data["loan_amount"] = numbers[0]
                
                if "salary" in text_lower or "income" in text_lower:
                    if "monthly_salary" in schema:
                        # If we have 2 numbers and one was loan, other might be salary
                        # If we only have 1 number, context decides
                        val = numbers[0]
                        if "loan_amount" in mock_data and len(numbers) > 1:
                            val = numbers[1]
                        mock_data["monthly_salary"] = val

            # Mock string fields if present in text
            if "name" in schema and ("name is" in text_lower or "i am" in text_lower):
                # Very basic name extraction or fallback
                mock_data["name"] = "Test User" 
            
            if "employment_type" in schema:
                if "salaried" in text_lower:
                    mock_data["employment_type"] = "Salaried"
                elif "business" in text_lower or "self" in text_lower:
                    mock_data["employment_type"] = "Self-Employed"
            
            return mock_data

        system_prompt = """You are a data extraction assistant. Extract structured information from user messages.
        Return ONLY valid JSON, no additional text or explanation."""
        
        schema_description = json.dumps(schema, indent=2)
        
        prompt = f"""Extract the following information from this user message:
        
        Schema:
        {schema_description}
        
        User message: "{text}"
        
        Return a JSON object with the extracted fields. Use null for missing values.
        Example: {{"name": "John Doe", "loan_amount": 500000, "monthly_salary": 50000}}
        """
        
        try:
            response = await self.chat(
                system_prompt=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            # Use regex to find JSON in the response
            import re
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in Claude's response")
            
            return json.loads(json_match.group(0))
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Claude response: {e}")
            raise ValueError(f"Invalid JSON response from Claude: {e}") from e
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            raise
    
    async def get_completion(self, prompt: str, system_prompt: str = None) -> str:
        """Legacy method for backward compatibility"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(system_prompt or "", messages)
