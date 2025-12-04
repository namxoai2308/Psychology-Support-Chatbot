"""Document schemas"""
from pydantic import BaseModel
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    id: int
    filename: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
