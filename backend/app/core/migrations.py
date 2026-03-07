"""Database migration utilities"""
import logging
from sqlalchemy import text, inspect
from app.core.database import engine
from app.core.config import settings

logger = logging.getLogger(__name__)


def check_and_add_sources_column():
    """Check if sources column exists in chat_messages, add if not"""
    try:
        # Get database URL to determine database type
        db_url = settings.DATABASE_URL
        
        with engine.begin() as conn:
            # Check database type
            # Hỗ trợ cả dạng postgresql:// và postgresql+psycopg2://
            if db_url.startswith("postgresql") or db_url.startswith("postgres://"):
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='chat_messages' AND column_name='sources'
                """))
                exists = result.fetchone() is not None
                
                if not exists:
                    logger.info("Adding 'sources' column to chat_messages table (PostgreSQL)...")
                    conn.execute(text("""
                        ALTER TABLE chat_messages 
                        ADD COLUMN sources JSONB
                    """))
                    logger.info("✅ Added 'sources' column successfully")
                else:
                    logger.debug("Column 'sources' already exists")
                    
            elif db_url.startswith("sqlite:///"):
                # SQLite
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('chat_messages')]
                
                if 'sources' not in columns:
                    logger.info("Adding 'sources' column to chat_messages table (SQLite)...")
                    conn.execute(text("""
                        ALTER TABLE chat_messages 
                        ADD COLUMN sources TEXT
                    """))
                    logger.info("✅ Added 'sources' column successfully")
                else:
                    logger.debug("Column 'sources' already exists")
            else:
                logger.warning(f"Unknown database type: {db_url}")
                
    except Exception as e:
        logger.error(f"Error checking/adding sources column: {e}")
        # Don't raise - allow app to continue even if migration fails
        # Admin can run manual migration if needed


def check_and_add_risk_flag_column():
    """Check if has_risk_flag column exists in chat_sessions, add if not"""
    try:
        db_url = settings.DATABASE_URL

        with engine.begin() as conn:
            # Hỗ trợ cả dạng postgresql:// và postgresql+psycopg2://
            if db_url.startswith("postgresql") or db_url.startswith("postgres://"):
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='chat_sessions' AND column_name='has_risk_flag'
                """))
                exists = result.fetchone() is not None

                if not exists:
                    logger.info("Adding 'has_risk_flag' column to chat_sessions table (PostgreSQL)...")
                    conn.execute(text("""
                        ALTER TABLE chat_sessions
                        ADD COLUMN has_risk_flag BOOLEAN DEFAULT FALSE
                    """))
                    logger.info("✅ Added 'has_risk_flag' column successfully")
                else:
                    logger.debug("Column 'has_risk_flag' already exists")

            elif db_url.startswith("sqlite:///"):
                # SQLite
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('chat_sessions')]

                if 'has_risk_flag' not in columns:
                    logger.info("Adding 'has_risk_flag' column to chat_sessions table (SQLite)...")
                    conn.execute(text("""
                        ALTER TABLE chat_sessions
                        ADD COLUMN has_risk_flag INTEGER DEFAULT 0
                    """))
                    logger.info("✅ Added 'has_risk_flag' column successfully")
                else:
                    logger.debug("Column 'has_risk_flag' already exists")
            else:
                logger.warning(f"Unknown database type: {db_url}")

    except Exception as e:
        logger.error(f"Error checking/adding has_risk_flag column: {e}")


def check_and_add_ratings_table():
    """Check if ratings table exists, create if not"""
    try:
        db_url = settings.DATABASE_URL
        
        with engine.begin() as conn:
            # Hỗ trợ cả dạng postgresql:// và postgresql+psycopg2://
            if db_url.startswith("postgresql") or db_url.startswith("postgres://"):
                # PostgreSQL - check if table exists
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name='ratings'
                """))
                exists = result.fetchone() is not None
                
                if not exists:
                    logger.info("Creating 'ratings' table (PostgreSQL)...")
                    conn.execute(text("""
                        CREATE TABLE ratings (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            rating INTEGER NOT NULL,
                            feedback TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    """))
                    conn.execute(text("CREATE INDEX idx_ratings_user_id ON ratings(user_id)"))
                    logger.info("✅ Created 'ratings' table successfully")
                else:
                    logger.debug("Table 'ratings' already exists")
                    
            elif db_url.startswith("sqlite:///"):
                # SQLite
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                if 'ratings' not in tables:
                    logger.info("Creating 'ratings' table (SQLite)...")
                    conn.execute(text("""
                        CREATE TABLE ratings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            rating INTEGER NOT NULL,
                            feedback TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    """))
                    conn.execute(text("CREATE INDEX idx_ratings_user_id ON ratings(user_id)"))
                    logger.info("✅ Created 'ratings' table successfully")
                else:
                    logger.debug("Table 'ratings' already exists")
                    
    except Exception as e:
        logger.error(f"Error checking/creating ratings table: {e}")


def run_migrations():
    """Run all migrations"""
    logger.info("Running database migrations...")
    check_and_add_sources_column()
    check_and_add_ratings_table()
    check_and_add_risk_flag_column()
    logger.info("Migrations completed")

