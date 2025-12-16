from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()

class ConversationState(BaseModel):
    conversation_id: str
    stage: str  # GREETING, INFO_GATHERING, VERIFICATION, UNDERWRITING, DECISION, SANCTION, COMPLETED
    messages: List[Message] = []
    loan_application: "LoanApplication" = None # collected info (name, loan_amount, salary, etc.)
    documents: Dict[str, str] = {}  # uploaded files (doc_type: file_path or base64)
    decision: Optional[str] = None  # APPROVED, REJECTED, PENDING

class LoanApplication(BaseModel):
    name: Optional[str] = None
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    monthly_salary: Optional[float] = None
    employment_type: Optional[str] = None
    credit_score: Optional[int] = None
    existing_loans: Optional[float] = None
    pan_number: Optional[str] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    next_stage: Optional[str] = None

# Legacy models for backward compatibility
class MessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    stage: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str

class FileUploadResponse(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    file_info: Optional[Dict[str, Any]] = None
    doc_type: Optional[str] = None

