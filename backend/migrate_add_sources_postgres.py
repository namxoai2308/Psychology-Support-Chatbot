"""Migration script to add sources column to chat_messages table (PostgreSQL/SQLite compatible)"""
import os
import sys
from app.core.config import settings

def migrate():
    """Add sources column to chat_messages table"""
    db_url = settings.DATABASE_URL
    
    print(f"🔧 Migrating database: {db_url}")
    
    # Check if PostgreSQL or SQLite
    if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        # PostgreSQL
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            # Parse database URL
            parsed = urlparse(db_url)
            
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:] if parsed.path else None
            )
            conn.autocommit = False
            cursor = conn.cursor()
            
            try:
                # Check if column already exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='chat_messages' AND column_name='sources'
                """)
                
                if cursor.fetchone():
                    print("✅ Column 'sources' already exists. Migration not needed.")
                    return
                
                # Add sources column (JSONB for PostgreSQL)
                print("📝 Adding 'sources' column to chat_messages table...")
                cursor.execute("""
                    ALTER TABLE chat_messages 
                    ADD COLUMN sources JSONB
                """)
                
                conn.commit()
                print("✅ Migration completed successfully!")
                print("   Added column: chat_messages.sources (JSONB, nullable)")
                
            except Exception as e:
                conn.rollback()
                print(f"❌ Migration failed: {e}")
                raise
            finally:
                cursor.close()
                conn.close()
                
        except ImportError:
            print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
            sys.exit(1)
            
    elif db_url.startswith("sqlite:///"):
        # SQLite
        import sqlite3
        
        db_path = db_url.replace("sqlite:///", "")
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
    else:
        print(f"❌ Unsupported database URL format: {db_url}")
        sys.exit(1)


if __name__ == "__main__":
    migrate()

