"""
Database connection utilities for the medical telegram warehouse.
"""
import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.user = os.getenv('DB_USER', 'medical_user')
        self.password = os.getenv('DB_PASSWORD', 'medical_pass')
        self.database = os.getenv('DB_NAME', 'medical_warehouse')
        
        self.connection_string = (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
        self.engine = None
        
    def connect(self):
        """Create database connection."""
        try:
            self.engine = create_engine(self.connection_string)
            logger.info(f"Connected to database {self.database}")
            return self.engine
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        if not self.engine:
            self.connect()
        
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results."""
        with self.get_connection() as conn:
            result = conn.execute(text(query), params or {})
            return result
    
    def create_raw_table(self):
        """Create the raw messages table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            message_id BIGINT PRIMARY KEY,
            channel_name VARCHAR(255),
            message_date TIMESTAMP,
            message_text TEXT,
            has_media BOOLEAN,
            image_path VARCHAR(500),
            views INTEGER,
            forwards INTEGER,
            raw_data JSONB,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_channel_date 
        ON raw.telegram_messages(channel_name, message_date);
        
        CREATE INDEX IF NOT EXISTS idx_message_date 
        ON raw.telegram_messages(message_date);
        """
        
        with self.get_connection() as conn:
            # Create schema if it doesn't exist
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("Raw table created/verified successfully")