"""Main FastAPI application"""
from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.migrations import run_migrations

logger = logging.getLogger(__name__)


def create_default_admin_user():
    """Tạo tài khoản giáo viên mặc định admin/admin nếu chưa tồn tại."""
    from app.models.models import User
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                username="admin",
                full_name="Giáo viên quản trị",
                role="teacher",
                hashed_password=get_password_hash("admin"),
            )
            db.add(admin)
            db.commit()
            logger.info("✅ Created default admin teacher user 'admin' (password: 'admin').")
        else:
            # Đảm bảo tài khoản admin luôn là giáo viên
            updated = False
            if admin.role != "teacher":
                admin.role = "teacher"
                updated = True
            if updated:
                db.commit()
                logger.info("✅ Ensured 'admin' user has teacher role.")
    except Exception as e:
        logger.error(f"❌ Error creating default admin user: {e}")
    finally:
        db.close()


# Create database tables, run migrations and seed default admin
Base.metadata.create_all(bind=engine)
run_migrations()
create_default_admin_user()

# Initialize FastAPI app
app = FastAPI(
    title="Student Chatbot API",
    description="AI-powered chatbot for student psychological support",
    version="2.0.0"
)

# CORS middleware
allowed_origins = [
    "http://localhost:3000",
    "https://psychology-support-chatbot.vercel.app",
]
if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
    if settings.FRONTEND_URL not in allowed_origins:
        allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routers import auth_router, chat_router, teacher_router, document_router

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(teacher_router.router)
app.include_router(document_router.router)


@app.get("/")
def root():
    """API health check"""
    return {
        "message": "Student Chatbot API",
        "version": "2.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


