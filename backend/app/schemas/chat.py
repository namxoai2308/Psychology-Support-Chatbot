"""Chat session and message schemas"""
from pydantic import BaseModel, field_validator
from typing import Optional, List, Union
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str


class DocumentSource(BaseModel):
    """Schema for document source"""
    id: int
    filename: str


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    role: str
    content: str
    created_at: datetime
    sources: List[DocumentSource] = []  # Document sources if AI used RAG
    
    @field_validator('sources', mode='before')
    @classmethod
    def parse_sources(cls, v):
        """Parse sources from JSON/dict to DocumentSource list"""
        if v is None:
            return []
        if isinstance(v, list):
            # Already a list, validate each item
            return [DocumentSource(**item) if isinstance(item, dict) else item for item in v]
        return []
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session"""
    title: Optional[str] = "Cuộc trò chuyện mới"


class ChatSessionResponse(BaseModel):
    """Schema for chat session response with messages"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """Schema for chat session list item"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None
    
    class Config:
        from_attributes = True
