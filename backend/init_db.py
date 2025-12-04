"""Initialize database tables"""
from app.core.database import engine, Base
from app.models.models import User, ChatSession, ChatMessage, SchoolDocument, DocumentChunk

print("🔧 Creating database tables...")

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Database tables created successfully!")
print("\nTables created:")
print("  - users")
print("  - chat_sessions")
print("  - chat_messages")
print("  - school_documents")
print("  - document_chunks (NEW! ⭐)")
print("\n🎉 Database ready!")






