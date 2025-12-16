from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/loan_ai_db")

# For async operations (recommended for FastAPI)
# Convert postgresql:// to postgresql+asyncpg://
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Only create async engine if USE_DATABASE is enabled
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"

if USE_DATABASE:
    try:
        # Async engine
        async_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=os.getenv("ENVIRONMENT", "development") == "development",
            future=True,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20
        )
        
        # Async session factory
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    except Exception as e:
        print(f"Warning: Could not create async engine: {e}")
        async_engine = None
        AsyncSessionLocal = None
else:
    async_engine = None
    AsyncSessionLocal = None

# Sync engine for migrations
try:
    sync_engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("ENVIRONMENT", "development") == "development"
    )
    
    # Sync session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine
    )
except Exception as e:
    print(f"Warning: Could not create sync engine: {e}")
    sync_engine = None
    SessionLocal = None

# Dependency for FastAPI
async def get_db():
    """Get database session"""
    if not USE_DATABASE or AsyncSessionLocal is None:
        # Return a dummy session that doesn't do anything
        class DummySession:
            async def commit(self): pass
            async def rollback(self): pass
            async def close(self): pass
            async def execute(self, stmt): 
                class DummyResult:
                    def scalar_one_or_none(self): return None
                    def scalar(self): return None
                return DummyResult()
            async def flush(self): pass
            def add(self, obj): pass
            async def refresh(self, obj): pass
        yield DummySession()
    else:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

def get_sync_db():
    """Get synchronous database session (for migrations)"""
    if not USE_DATABASE or SessionLocal is None:
        class DummySession:
            def close(self): pass
        yield DummySession()
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

