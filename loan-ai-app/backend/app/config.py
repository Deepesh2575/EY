from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from functools import lru_cache
from typing import List
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "AI Loan Assistant"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = True

    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/loan_ai_db")

    # Auth
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # Claude
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3002", "http://localhost:3003"]

    # File Upload
    upload_dir: Path = BASE_DIR / "uploads"
    generated_docs_dir: Path = BASE_DIR / "generated_docs"
    max_file_size: int = 5242880  # 5MB

    # Server
    port: int = 8000
    host: str = "0.0.0.0"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Monitoring (optional)
    sentry_dsn: str = ""

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_api_key(cls, v):
        # Allow empty API key in settings — services will handle mock/fallback behavior.
        return v



@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

