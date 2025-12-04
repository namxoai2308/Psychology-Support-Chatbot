from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, ChatSession, ChatMessage
from app.schemas import (
    ChatSessionCreate, 
    ChatSessionResponse, 
    MessageCreate, 
    MessageResponse,
    ChatSessionListResponse
)
from app.services.gemini import gemini_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    new_session = ChatSession(
        user_id=current_user.id,
        title=session_data.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/sessions", response_model=List[ChatSessionListResponse])
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for current user"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    
    result = []
    for session in sessions:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at.desc()).all()
        
        result.append({
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(messages),
            "last_message": messages[0].content if messages else None
        })
    
    return result


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session with all messages"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def send_message(
    session_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat session and get AI response"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    
    # Get chat history
    chat_history = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    history_for_ai = [
        {"role": msg.role, "content": msg.content} 
        for msg in chat_history[:-1]  # Exclude the current message
    ]
    
    # Generate AI response with Simple RAG (no embedding API needed!)
    ai_response_text = gemini_service.generate_response(
        message_data.content,
        history_for_ai,
        db  # Pass database session for RAG search
    )
    
    # Save AI response
    ai_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_response_text
    )
    db.add(ai_message)
    
    # Update session timestamp and title if first message
    session.updated_at = datetime.utcnow()
    if len(chat_history) == 1:  # First message
        session.title = gemini_service.generate_chat_title(message_data.content)
    
    db.commit()
    db.refresh(ai_message)
    
    return ai_message


@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}


