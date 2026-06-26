"""
Script to load raw Telegram data from the data lake into PostgreSQL.
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import text
from dotenv import load_dotenv

# Add the src directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RawDataLoader:
    """Load raw data from JSON files into PostgreSQL."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.data_dir = Path('data/raw/telegram_messages')
        
    def read_json_files(self) -> List[Dict[str, Any]]:
        """
        Read all JSON files from the data lake.
        
        Returns:
            List of message dictionaries
        """
        all_messages = []
        
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist")
            return all_messages
            
        # Walk through the directory structure
        for date_dir in self.data_dir.iterdir():
            if not date_dir.is_dir():
                continue
                
            for json_file in date_dir.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        all_messages.extend(messages)
                        logger.info(
                            f"Loaded {len(messages)} messages from {json_file}"
                        )
                except Exception as e:
                    logger.error(f"Error reading {json_file}: {e}")
                    
        logger.info(f"Total messages loaded: {len(all_messages)}")
        return all_messages
        
    def load_to_postgres(self, messages: List[Dict[str, Any]]):
        """
        Load messages into PostgreSQL.
        
        Args:
            messages: List of message dictionaries
        """
        if not messages:
            logger.warning("No messages to load")
            return
            
        # Create the raw table
        self.db.create_raw_table()
        
        # Prepare the insert statement
        insert_sql = """
        INSERT INTO raw.telegram_messages (
            message_id,
            channel_name,
            message_date,
            message_text,
            has_media,
            image_path,
            views,
            forwards,
            raw_data
        ) VALUES (
            :message_id,
            :channel_name,
            :message_date,
            :message_text,
            :has_media,
            :image_path,
            :views,
            :forwards,
            :raw_data
        )
        ON CONFLICT (message_id) DO UPDATE SET
            views = EXCLUDED.views,
            forwards = EXCLUDED.forwards,
            image_path = EXCLUDED.image_path,
            raw_data = EXCLUDED.raw_data;
        """
        
        # Insert messages in batches
        batch_size = 100
        total_inserted = 0
        
        with self.db.get_connection() as conn:
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                try:
                    # Convert data types
                    for msg in batch:
                        msg['message_date'] = datetime.fromisoformat(
                            msg['message_date']
                        )
                        msg['raw_data'] = json.dumps(msg.get('raw_data', {}))
                        
                    conn.execute(text(insert_sql), batch)
                    conn.commit()
                    total_inserted += len(batch)
                    logger.info(f"Inserted batch of {len(batch)} messages")
                    
                except Exception as e:
                    logger.error(f"Error inserting batch: {e}")
                    conn.rollback()
                    
        logger.info(f"Total messages loaded: {total_inserted}")
        
    def run(self):
        """Run the full loading process."""
        logger.info("Starting raw data loading process")
        
        # Read data from JSON files
        messages = self.read_json_files()
        
        # Load to PostgreSQL
        self.load_to_postgres(messages)
        
        logger.info("Raw data loading complete")

def main():
    """Main entry point."""
    loader = RawDataLoader()
    loader.run()

if __name__ == "__main__":
    main()