"""Pydantic schemas for request/response validation"""
from app.schemas.auth import (
    UserBase,
    UserCreate,
    UserResponse,
    UserLogin,
    Token
)
from app.schemas.chat import (
    MessageCreate,
    MessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse
)
from app.schemas.document import DocumentUploadResponse
from app.schemas.teacher import StudentChatHistoryResponse

__all__ = [
    # Auth
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "Token",
    # Chat
    "MessageCreate",
    "MessageResponse",
    "ChatSessionCreate",
    "ChatSessionResponse",
    "ChatSessionListResponse",
    # Document
    "DocumentUploadResponse",
    # Teacher
    "StudentChatHistoryResponse"
]
