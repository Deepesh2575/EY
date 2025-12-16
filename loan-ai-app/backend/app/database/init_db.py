"""
Initialize database tables
Run this script to create all database tables
"""
from sqlalchemy import create_engine
from app.database.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize database tables"""
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/loan_ai_db")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    print(f"✅ Connected to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

if __name__ == "__main__":
    init_database()


