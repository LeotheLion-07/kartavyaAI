from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kartavya AI"
    TAGLINE: str = "Pass on what matters, with proof."
    VERSION: str = "2.4.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "kartavya-super-secure-jwt-secret-key-production-grade-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database: Default to local SQLite for instant zero-dependency execution, configurable to PostgreSQL + pgvector
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kartavya.db")
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    
    # Redis / Celery settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    class Config:
        case_sensitive = True

settings = Settings()
