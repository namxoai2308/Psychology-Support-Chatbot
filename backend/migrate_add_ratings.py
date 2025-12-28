"""Migration script to add ratings table"""
import sqlite3
import os
from app.core.config import settings

def migrate():
    """Add ratings table"""
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        db_path = "chatbot.db"
    
    print(f"🔧 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ratings'")
        if cursor.fetchone():
            print("✅ Table 'ratings' already exists. Migration not needed.")
            return
        
        # Create ratings table
        print("📝 Creating 'ratings' table...")
        cursor.execute("""
            CREATE TABLE ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                feedback TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create index on user_id
        cursor.execute("CREATE INDEX idx_ratings_user_id ON ratings(user_id)")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   Created table: ratings")
        print("   Created index: idx_ratings_user_id")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()

