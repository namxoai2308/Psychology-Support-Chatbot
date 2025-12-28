"""Rating schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingCreate(BaseModel):
    """Schema for creating a rating"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    feedback: Optional[str] = None


class RatingResponse(BaseModel):
    """Schema for rating response"""
    id: int
    rating: int
    feedback: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageCountResponse(BaseModel):
    """Schema for message count response"""
    total_messages: int
    should_show_rating: bool  # True if 10-15 messages and not rated yet

