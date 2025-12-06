"""Application configuration and settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys - Support multiple keys for rotation (up to 15 keys)
    GEMINI_API_KEY: str
    GEMINI_API_KEY_2: Optional[str] = None
    GEMINI_API_KEY_3: Optional[str] = None
    GEMINI_API_KEY_4: Optional[str] = None
    GEMINI_API_KEY_5: Optional[str] = None
    GEMINI_API_KEY_6: Optional[str] = None
    GEMINI_API_KEY_7: Optional[str] = None
    GEMINI_API_KEY_8: Optional[str] = None
    GEMINI_API_KEY_9: Optional[str] = None
    GEMINI_API_KEY_10: Optional[str] = None
    GEMINI_API_KEY_11: Optional[str] = None
    GEMINI_API_KEY_12: Optional[str] = None
    GEMINI_API_KEY_13: Optional[str] = None
    GEMINI_API_KEY_14: Optional[str] = None
    GEMINI_API_KEY_15: Optional[str] = None
    
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
