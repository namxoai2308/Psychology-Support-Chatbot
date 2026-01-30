"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


db_url = settings.DATABASE_URL

# Detect database type
is_sqlite = db_url.startswith("sqlite:///")
is_postgres = db_url.startswith("postgresql://") or db_url.startswith("postgres://")

# Base connect args
connect_args = {}

if is_sqlite:
    # SQLite needs this flag when used with multiple threads (FastAPI default)
    connect_args = {"check_same_thread": False}
elif is_postgres:
    # Render PostgreSQL thường yêu cầu SSL, đảm bảo sslmode=require nếu chưa có
    if "sslmode=" not in db_url:
        db_url = f"{db_url}?sslmode=require"

# Create database engine
engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # tránh lỗi connection bị đóng đột ngột
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
