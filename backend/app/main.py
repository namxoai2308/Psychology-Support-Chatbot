"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Student Chatbot API",
    description="AI-powered chatbot for student psychological support",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
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


