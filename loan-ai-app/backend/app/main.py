from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import os
import uuid
from typing import Optional
from datetime import datetime

from app.config import settings
from app.utils.logger import logger
from app.models import (
    MessageRequest, 
    MessageResponse, 
    ConversationResponse,
    FileUploadResponse
)
from app.agents.master_agent import MasterAgent
from app.database.connection import get_db
from app.database.models import Conversation as DBConversation, Message as DBMessage, Document as DBDocument
from app.database.adapter import db_conversation_to_state
from app.routers.auth import router as auth_router
from app.services.ocr_service import extract_text_from_bytes, parse_key_fields
from app.services.auth_service import get_current_active_user, get_optional_user
from app.database.models import User

# Initialize FastAPI app
app = FastAPI(
    title="AI Loan Sales Platform API",
    description="Multi-agent conversational loan sales platform",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)

# Initialize master agent (still used for processing, but data stored in DB)
master_agent = MasterAgent()

# Use database flag (can be toggled via environment)
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

async def get_current_user_or_none(current_user: Optional[User] = Depends(get_optional_user)):
    if REQUIRE_AUTH and not current_user:
         # If auth is required but no user found (and optional_user returned None)
         # We implicitly require auth if REQUIRE_AUTH is true
         # But get_optional_user won't raise 401. 
         # So we must raise it here if REQUIRE_AUTH is True and user is missing.
         raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        if USE_DATABASE:
            # Check database connection
            result = await db.execute(select(func.count(DBConversation.id)))
            total_conversations = result.scalar() or 0
        else:
            total_conversations = len(master_agent.conversations)
        
        return {
            "status": "healthy",
            "service": "AI Loan Sales Platform API",
            "version": "3.0.0",
            "timestamp": datetime.now().isoformat(),
            "database_enabled": USE_DATABASE,
            "active_conversations": total_conversations
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "database_enabled": USE_DATABASE
        }

@app.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get platform statistics"""
    try:
        if USE_DATABASE:
            # Get stats from database
            total_result = await db.execute(select(func.count(DBConversation.id)))
            total_conversations = total_result.scalar() or 0
            
            approved_result = await db.execute(
                select(func.count(DBConversation.id)).where(DBConversation.decision == "APPROVED")
            )
            approved_loans = approved_result.scalar() or 0
            
            rejected_result = await db.execute(
                select(func.count(DBConversation.id)).where(DBConversation.decision == "REJECTED")
            )
            rejected_loans = rejected_result.scalar() or 0
            
            pending_result = await db.execute(
                select(func.count(DBConversation.id)).where(DBConversation.decision.is_(None))
            )
            pending = pending_result.scalar() or 0
        else:
            # Fallback to in-memory
            conversations = master_agent.conversations
            total_conversations = len(conversations)
            approved_loans = sum(1 for c in conversations.values() if c.decision == "APPROVED")
            rejected_loans = sum(1 for c in conversations.values() if c.decision == "REJECTED")
            pending = sum(1 for c in conversations.values() if c.decision is None)
        
        return {
            "total_conversations": total_conversations,
            "approved_loans": approved_loans,
            "rejected_loans": rejected_loans,
            "pending": pending,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/applications")
async def get_applications(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    skip: int = 0
):
    """Get list of loan applications for dashboard"""
    try:
        if USE_DATABASE:
            # Fetch detailed applications from DB
            query = select(DBConversation).order_by(DBConversation.created_at.desc()).offset(skip).limit(limit)
            result = await db.execute(query)
            conversations = result.scalars().all()
            
            apps = []
            for conv in conversations:
                state = db_conversation_to_state(conv)
                app_data = state.loan_application.dict() if state.loan_application else {}
                apps.append({
                    "id": conv.id,
                    "name": app_data.get("name", "N/A"),
                    "amount": app_data.get("loan_amount"),
                    "status": conv.decision or "IN_PROGRESS",
                    "stage": conv.stage,
                    "date": conv.created_at.isoformat() if conv.created_at else None,
                    "score": 750, # Mock credit score
                    "type": app_data.get("loan_purpose", "Personal")
                })
            return apps
        else:
            # In-memory
            apps = []
            for conv in list(master_agent.conversations.values())[skip:skip+limit]:
                app_data = conv.loan_application.dict() if conv.loan_application else {}
                apps.append({
                    "id": conv.conversation_id,
                    "name": app_data.get("name", "N/A"),
                    "amount": app_data.get("loan_amount"),
                    "status": conv.decision or "IN_PROGRESS",
                    "stage": conv.stage,
                    "date": datetime.now().isoformat(), # Mock date for in-memory
                    "score": 750,
                    "type": app_data.get("loan_purpose", "Personal")
                })
            return apps
            
    except Exception as e:
        logger.error(f"Admin apps error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=MessageResponse)
async def chat(
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none)
):
    """
    Main chat endpoint - processes messages through Master Agent
    
    Body:
        message: User message
        conversation_id: Optional conversation ID (creates new if not provided)
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        conversation_state = None
        
        if USE_DATABASE:
            # Get or create conversation from database
            result = await db.execute(
                select(DBConversation).where(DBConversation.id == conversation_id)
            )
            db_conv = result.scalar_one_or_none()
            
            if db_conv:
                conversation_state = db_conversation_to_state(db_conv)
            else:
                # Create new conversation
                db_conv = DBConversation(
                    id=conversation_id,
                    stage="GREETING"
                )
                db.add(db_conv)
                await db.flush()
                conversation_state = db_conversation_to_state(db_conv)
        else:
            # Fallback to in-memory
            if request.conversation_id:
                conversation_state = master_agent.get_conversation_state(request.conversation_id)
            if not conversation_state:
                conversation_id = master_agent.create_conversation()
                conversation_state = master_agent.get_conversation_state(conversation_id)
        
        # Process message through Master Agent
        result = await master_agent.process_message(conversation_state, request.message)
        
        # Save to database
        if USE_DATABASE:
            # Update conversation
            result_db = await db.execute(
                select(DBConversation).where(DBConversation.id == conversation_id)
            )
            db_conv = result_db.scalar_one()
            db_conv.stage = result["next_stage"]
            db_conv.decision = conversation_state.decision
            db_conv.user_data = conversation_state.user_data
            
            # Save user message
            user_msg = DBMessage(
                conversation_id=conversation_id,
                role="user",
                content=request.message
            )
            db.add(user_msg)
            
            # Save bot response
            bot_msg = DBMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=result["response"],
                metadata={"stage": result["next_stage"], "decision": conversation_state.decision}
            )
            db.add(bot_msg)
            
            await db.commit()
        
        # Determine if this is a decision message
        is_decision = conversation_state.decision in ["APPROVED", "REJECTED"]
        
        # Construct sanction letter URL if generated
        sanction_letter_url = None
        if result.get("sanction_letter_path"):
            sanction_letter_url = f"/api/download/{os.path.basename(result['sanction_letter_path'])}"
        
        return MessageResponse(
            message=result["response"],
            conversation_id=conversation_id,
            metadata={
                "stage": result["next_stage"],
                "decision": conversation_state.decision,
                "is_decision": is_decision,
                "message_count": len(conversation_state.messages),
                "sanction_letter_url": sanction_letter_url
            },
            timestamp=datetime.now().isoformat(),
            stage=result["next_stage"]
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        if USE_DATABASE:
            await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "An error occurred processing your message",
                "error": str(e)
            }
        )

@app.post("/chat/message", response_model=MessageResponse)
async def send_message(request: MessageRequest, db: AsyncSession = Depends(get_db)):
    """Legacy endpoint for backward compatibility"""
    return await chat(request, db)

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Query(None),
    doc_type: str = Query("salary_slip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none)
):
    """Upload a document for verification"""
    try:
        conversation_state = None
        
        if USE_DATABASE:
            # Get or create conversation from DB
            if conversation_id:
                result = await db.execute(select(DBConversation).where(DBConversation.id == conversation_id))
                db_conv = result.scalar_one_or_none()
            else:
                db_conv = None
                
            if not db_conv:
                conversation_id = conversation_id or str(uuid.uuid4())
                db_conv = DBConversation(id=conversation_id, stage="GREETING")
                db.add(db_conv)
                await db.flush()
            
            conversation_state = db_conversation_to_state(db_conv)
        else:
            # In-memory fallback
            if not conversation_id:
                conversation_id = master_agent.create_conversation()
            
            conversation_state = master_agent.get_conversation_state(conversation_id)
            if not conversation_state:
                # Handle case where ID provided but not found in memory
                conversation_id = master_agent.create_conversation()
                conversation_state = master_agent.get_conversation_state(conversation_id)
        
        # Read file content
        contents = await file.read()
        file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents)
        }
        
        # Save file (in production, use cloud storage)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = settings.upload_dir / f"{conversation_id}_{doc_type}_{file.filename}"
        file_path.write_bytes(contents)
        
        # Process file through master agent
        response = await master_agent.process_file(
            conversation_state=conversation_state,
            file_info=file_info,
            file_content=contents,
            doc_type=doc_type
        )
        
        # Save document to database
        if USE_DATABASE:
            db_doc = DBDocument(
                conversation_id=conversation_id,
                doc_type=doc_type,
                filename=file.filename,
                file_path=str(file_path),
                file_size=len(contents),
                mime_type=file.content_type
            )
            db.add(db_doc)
            await db.commit()
        
        return FileUploadResponse(
            message=response.get("message", "File uploaded successfully"),
            conversation_id=conversation_id,
            file_info=file_info,
            doc_type=doc_type
        )
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        if USE_DATABASE:
            await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/ocr')
async def ocr_extract(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none)
):
    """Extract text from uploaded image and return parsed fields."""
    try:
        contents = await file.read()
        text = extract_text_from_bytes(contents)
        parsed = parse_key_fields(text)

        # Optionally attach to conversation state (in-memory)
        if not USE_DATABASE and conversation_id:
            conv = master_agent.get_conversation_state(conversation_id)
            if conv:
                conv.documents[file.filename] = {"ocr_text": text, "parsed": parsed}

        return {
            "filename": file.filename,
            "text": text,
            "fields": parsed
        }
    except Exception as e:
        logger.error(f"OCR endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/upload")
async def upload_file_legacy(
    file: UploadFile = File(...), 
    conversation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Legacy upload endpoint"""
    return await upload_document(file, conversation_id, "salary_slip", db)

@app.post("/api/conversation", response_model=ConversationResponse)
async def create_conversation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none)
):
    """Create a new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        
        if USE_DATABASE:
            db_conv = DBConversation(id=conversation_id)
            db.add(db_conv)
            await db.commit()
        else:
            conversation_id = master_agent.create_conversation()
        
        return ConversationResponse(conversation_id=conversation_id)
    except Exception as e:
        if USE_DATABASE:
            await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/conversation", response_model=ConversationResponse)
async def create_conversation_legacy(db: AsyncSession = Depends(get_db)):
    """Legacy endpoint for creating conversation"""
    return await create_conversation(db)

@app.get("/api/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none)
):
    """Retrieve full conversation history and state"""
    try:
        if USE_DATABASE:
            result = await db.execute(
                select(DBConversation).where(DBConversation.id == conversation_id)
            )
            db_conv = result.scalar_one_or_none()
            
            if not db_conv:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            conversation_state = db_conversation_to_state(db_conv)
        else:
            conversation_state = master_agent.get_conversation_state(conversation_id)
            if not conversation_state:
                raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation_id": conversation_state.conversation_id,
            "stage": conversation_state.stage,
            "decision": conversation_state.decision,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
                }
                for msg in conversation_state.messages
            ],
            "user_data": conversation_state.user_data,
            "documents": list(conversation_state.documents.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/conversation/{conversation_id}")
async def get_conversation_legacy(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Legacy endpoint for getting conversation"""
    return await get_conversation(conversation_id, db)

@app.get("/api/download/{filename:path}")
async def download_sanction_letter(
    filename: str,
    current_user: User = Depends(get_current_user_or_none)
):
    """Download generated sanction letter PDF"""
    try:
        # Sanitize filename to prevent path traversal
        secure_filename = os.path.basename(filename)
        file_path = (settings.generated_docs_dir / secure_filename).resolve()

        # Double-check that the resolved path is within the generated docs directory
        if not str(file_path).startswith(str(settings.generated_docs_dir.resolve())):
            raise HTTPException(status_code=403, detail="Forbidden")

        if file_path.exists() and file_path.is_file():
            return FileResponse(
                file_path,
                media_type="application/pdf",
                filename=secure_filename
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "An error occurred"),
            "error": str(exc.detail) if isinstance(exc.detail, str) else exc.detail.get("error", "")
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "error": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
