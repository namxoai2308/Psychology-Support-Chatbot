"""Migration script to add sources column to chat_messages table"""
import sqlite3
import os
from app.core.config import settings

def migrate():
    """Add sources column to chat_messages table"""
    # Get database path from DATABASE_URL
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        db_path = "chatbot.db"
    
    print(f"🔧 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sources' in columns:
            print("✅ Column 'sources' already exists. Migration not needed.")
            return
        
        # Add sources column
        print("📝 Adding 'sources' column to chat_messages table...")
        cursor.execute("""
            ALTER TABLE chat_messages 
            ADD COLUMN sources TEXT
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   Added column: chat_messages.sources (TEXT, nullable)")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()

