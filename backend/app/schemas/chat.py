"""Chat session and message schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    role: str
    content: str
    created_at: datetime
    
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
