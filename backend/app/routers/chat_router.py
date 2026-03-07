from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user
from app.models.models import User, ChatSession, ChatMessage, Rating
from app.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    MessageCreate,
    MessageResponse,
    ChatSessionListResponse,
)
from app.schemas.rating import RatingCreate, RatingResponse, MessageCountResponse
from app.services.gemini import gemini_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


RISK_KEYWORDS = [
    # Tự tử / tự hại
    "tự tử",
    "tự sát",
    "muốn chết",
    "không muốn sống",
    "chết cho xong",
    "kết thúc cuộc đời",
    "tự làm đau mình",
    "tự làm đau bản thân",
    "cắt tay",
    "rạch tay",
    "tự hại",
]


def _detect_risk(text: str) -> bool:
    """Phát hiện nhanh nguy cơ tự hại/tự tử từ nội dung tin nhắn hiện tại"""
    if not text:
        return False
    lowered = text.lower()
    return any(kw in lowered for kw in RISK_KEYWORDS)


def _detect_stage(chat_history: List[ChatMessage]) -> int:
    """
    Xác định giai đoạn (1–4) dựa trên nội dung tin nhắn gần nhất.
    - Giai đoạn 1: tin nhắn đầu, chào hỏi / nêu vấn đề.
    - Giai đoạn 2: hỏi thêm, làm rõ vấn đề.
    - Giai đoạn 3: khi học sinh chủ động hỏi giải pháp / lời khuyên.
    - Giai đoạn 4: khi học sinh kết thúc / cảm ơn, sau khi đã hỏi giải pháp.
    """
    if not chat_history:
        return 1

    # Tìm tin nhắn user gần nhất
    last_user = next((m for m in reversed(chat_history) if m.role == "user"), None)
    if not last_user:
        return 1

    text = (last_user.content or "").lower()
    user_count = sum(1 for m in chat_history if m.role == "user")

    # Từ khóa yêu cầu giải pháp → chuyển sang giai đoạn 3
    solution_keywords = [
        "giải pháp",
        "lời khuyên",
        "phải làm sao",
        "con phải làm sao",
        "con nên làm gì",
        "có cách nào",
        "cô giúp con",
        "cô tư vấn cho con",
        "chỉ cho con",
        "hướng dẫn cho con",
    ]
    if any(kw in text for kw in solution_keywords):
        return 3

    # Từ khóa kết thúc / cảm ơn → giai đoạn 4 (nếu đã có ít nhất 2 lượt user)
    end_keywords = [
        "cảm ơn cô",
        "cảm ơn nhiều",
        "được rồi ạ",
        "con hiểu rồi",
        "vậy thôi ạ",
    ]
    if user_count >= 2 and any(kw in text for kw in end_keywords):
        return 4

    # Mặc định:
    # - Lượt user đầu tiên → giai đoạn 1
    # - Từ lượt thứ 2 trở đi (chưa hỏi giải pháp, chưa kết) → giai đoạn 2
    return 1 if user_count <= 1 else 2


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
    background_tasks: BackgroundTasks,
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

    # Đánh dấu cờ nguy cơ tự hại/tự tử trên phiên nếu phát hiện từ khóa nhạy cảm
    if _detect_risk(message_data.content):
        session.has_risk_flag = True

    # Xác định giai đoạn hiện tại (1–4) dựa trên nội dung cuộc trò chuyện
    stage = _detect_stage(chat_history)

    # Giai đoạn 1 & 2: API thuần, KHÔNG dùng chunk
    # Giai đoạn 3 & 4: BẬT chunk để lấy "tài liệu tham khảo"
    use_rag_for_sources = stage in (3, 4)
    db_for_rag = db if use_rag_for_sources else None

    # Giai đoạn 3: cho phép dùng chunk cả khi trả lời
    # Giai đoạn 1,2,4: trả lời API thuần (không trộn context)
    use_context_for_answer = (stage == 3)

    # Chỉ lưu "tài liệu tham khảo" ở giai đoạn 3 & 4
    ai_response_text, sources = gemini_service.generate_response(
        message_data.content,
        history_for_ai,
        db_for_rag,
        use_context_for_answer=use_context_for_answer,
    )
    sources_to_save = sources if (use_rag_for_sources and sources) else None

    # Log chi tiết để debug UI bị cắt text (chỉ dùng logger, không in ra terminal)
    from logging import getLogger

    _logger = getLogger(__name__)
    debug_len = len(ai_response_text or "")
    _logger.info(
        "🧠 Chat response | stage=%d | use_rag=%s | use_context_for_answer=%s | len=%d",
        stage,
        use_rag_for_sources,
        use_context_for_answer,
        debug_len,
    )
    _logger.info("📚 Chat sources (saved=%s): %s", bool(sources_to_save), sources_to_save)

    # --- Đoạn log in nội dung chat ra terminal (đã tắt để tránh spam) ---
    # print(
    #     f"[CHAT_DEBUG] stage={stage} use_rag={use_rag_for_sources} "
    #     f"use_context_for_answer={use_context_for_answer} len={debug_len} "
    #     f"text={ai_response_text!r}"
    # )
    # print(f"[CHAT_DEBUG] sources_saved={bool(sources_to_save)} sources={sources_to_save}")

    # Save AI response with sources (nếu có)
    ai_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_response_text,
        sources=sources_to_save
    )
    db.add(ai_message)
    
    # Update session timestamp and title if first message
    session.updated_at = datetime.utcnow()
    if len(chat_history) == 1:  # First message: đặt title tạm, trả response ngay; tạo title đẹp trong background
        session.title = (message_data.content[:50] + "…") if len(message_data.content) > 50 else message_data.content or "Cuộc trò chuyện mới"
        background_tasks.add_task(_update_session_title_later, session_id, message_data.content)

    db.commit()
    db.refresh(ai_message)

    return ai_message


def _update_session_title_later(session_id: int, first_message_content: str) -> None:
    """Background: gọi Gemini tạo title rồi cập nhật session (không chặn response)."""
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session and first_message_content:
            session.title = gemini_service.generate_chat_title(first_message_content)
            db.commit()
    except Exception:
        pass
    finally:
        db.close()


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


@router.get("/message-count", response_model=MessageCountResponse)
def get_message_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total message count for user and check if should show rating popup"""
    # Count total user messages (only user messages, not assistant)
    total_messages = db.query(func.count(ChatMessage.id)).join(
        ChatSession
    ).filter(
        ChatSession.user_id == current_user.id,
        ChatMessage.role == "user"
    ).scalar() or 0
    
    # Check if user has already rated
    has_rated = db.query(Rating).filter(
        Rating.user_id == current_user.id
    ).first() is not None
    
    # Show rating if 10-15 messages and not rated yet
    should_show_rating = 10 <= total_messages <= 15 and not has_rated
    
    return {
        "total_messages": total_messages,
        "should_show_rating": should_show_rating
    }


@router.post("/rating", response_model=RatingResponse)
def submit_rating(
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a rating for the chatbot"""
    # Check if user already rated
    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_data.rating
        existing_rating.feedback = rating_data.feedback
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    
    # Create new rating
    new_rating = Rating(
        user_id=current_user.id,
        rating=rating_data.rating,
        feedback=rating_data.feedback
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return new_rating


