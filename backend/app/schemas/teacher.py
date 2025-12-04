"""Teacher dashboard schemas"""
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.chat import ChatSessionResponse


class StudentChatHistoryResponse(BaseModel):
    """Schema for student chat history (teacher view)"""
    user_id: int
    username: str
    full_name: Optional[str]
    email: str
    sessions: List[ChatSessionResponse]
    
    class Config:
        from_attributes = True
