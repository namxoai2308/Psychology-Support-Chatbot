from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_teacher
from app.models.models import User, ChatSession, ChatMessage, Rating
from app.schemas import StudentChatHistoryResponse, ChatSessionResponse
from app.schemas.rating import RatingResponse

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


@router.get("/ratings", response_model=List[RatingResponse])
def get_all_ratings(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all ratings from students (teacher only)"""
    ratings = db.query(Rating).join(User).filter(
        User.role == "student"
    ).order_by(Rating.created_at.desc()).all()
    
    return ratings


@router.get("/ratings/stats")
def get_rating_stats(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get rating statistics (teacher only)"""
    total_ratings = db.query(func.count(Rating.id)).join(User).filter(
        User.role == "student"
    ).scalar() or 0
    
    if total_ratings == 0:
        return {
            "total_ratings": 0,
            "average_rating": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    avg_rating = db.query(func.avg(Rating.rating)).join(User).filter(
        User.role == "student"
    ).scalar() or 0
    
    # Get distribution
    distribution = {}
    for star in range(1, 6):
        count = db.query(func.count(Rating.id)).join(User).filter(
            User.role == "student",
            Rating.rating == star
        ).scalar() or 0
        distribution[star] = count
    
    return {
        "total_ratings": total_ratings,
        "average_rating": round(float(avg_rating), 2),
        "rating_distribution": distribution
    }




