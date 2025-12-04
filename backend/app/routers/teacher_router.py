from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_teacher
from app.models.models import User, ChatSession, ChatMessage
from app.schemas import StudentChatHistoryResponse, ChatSessionResponse

router = APIRouter(prefix="/api/teacher", tags=["Teacher Dashboard"])


@router.get("/students", response_model=List[StudentChatHistoryResponse])
def get_all_students_history(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get chat history of all students (teacher only)"""
    students = db.query(User).filter(User.role == "student").all()
    
    result = []
    for student in students:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == student.id
        ).order_by(ChatSession.updated_at.desc()).all()
        
        result.append({
            "user_id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "email": student.email,
            "sessions": sessions
        })
    
    return result


@router.get("/students/{student_id}/sessions", response_model=List[ChatSessionResponse])
def get_student_sessions(
    student_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a specific student (teacher only)"""
    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student"
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == student_id
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session_details(
    session_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get details of a specific chat session (teacher only)"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session




