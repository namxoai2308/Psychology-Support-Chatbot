"""Application configuration and settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    GEMINI_API_KEY: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # PDF Processing - Gemini Vision OCR for scanned PDFs
    USE_VISION_OCR: bool = False  # Enable for scanned PDFs
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000  # Larger chunks for better context
    CHUNK_OVERLAP: int = 200  # More overlap to preserve context
    TOP_K_CHUNKS: int = 5  # Top 5 most relevant chunks (increased)
    SIMILARITY_THRESHOLD: float = 0.08  # Lower threshold for more results
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
