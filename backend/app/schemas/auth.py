"""Authentication and user schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema (client không chọn vai trò, mặc định là học sinh)."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user (luôn đăng ký dưới vai trò học sinh)."""
    password: str


class UserResponse(UserBase):
    """Schema for user response (trả về thêm vai trò)."""
    id: int
    created_at: datetime
    role: str
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse
