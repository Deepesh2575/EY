from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True, index=True)  # For future auth
    stage = Column(String, default="GREETING")
    decision = Column(String, nullable=True)  # APPROVED, REJECTED
    user_data = Column(JSON, default=dict)  # Store collected user data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")
    loan_application = relationship("LoanApplication", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    conversation = relationship("Conversation", back_populates="messages")

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # User details
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Loan details
    loan_amount = Column(Float, nullable=True)
    loan_purpose = Column(String, nullable=True)
    monthly_salary = Column(Float, nullable=True)
    employment_type = Column(String, nullable=True)
    
    # Assessment
    credit_score = Column(Integer, nullable=True)
    existing_loans = Column(Float, default=0)
    approved_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    tenure_months = Column(Integer, nullable=True)
    monthly_emi = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="loan_application")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    doc_type = Column(String, nullable=False)  # salary_slip, pan_card, aadhaar, bank_statement
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Path to stored file
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="documents")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


