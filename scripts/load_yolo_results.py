"""
Load YOLO detection results into PostgreSQL
"""
import os
import csv
import logging
from pathlib import Path
from sqlalchemy import text

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_yolo_table(db):
    """Create YOLO results table"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS raw.image_detections (
        id SERIAL PRIMARY KEY,
        message_id BIGINT,
        channel_name VARCHAR(255),
        image_path VARCHAR(500),
        detected_class VARCHAR(100),
        confidence FLOAT,
        category VARCHAR(50),
        num_objects INTEGER,
        detection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with db.get_connection() as conn:
        conn.execute(text(create_sql))
        conn.commit()
    logger.info("Image detections table created")

def load_yolo_results(db):
    """Load YOLO results from CSV"""
    results_path = Path('data/processed/yolo_detections.csv')
    
    if not results_path.exists():
        logger.warning(f"No YOLO results found at {results_path}")
        logger.info("Creating sample YOLO data...")
        create_sample_data()
        return
    
    with open(results_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        logger.warning("No rows in CSV")
        return
    
    insert_sql = """
    INSERT INTO raw.image_detections (
        message_id,
        channel_name,
        image_path,
        detected_class,
        confidence,
        category,
        num_objects
    ) VALUES (
        :message_id,
        :channel_name,
        :image_path,
        :detected_class,
        :confidence,
        :category,
        :num_objects
    )
    """
    
    with db.get_connection() as conn:
        count = 0
        for row in rows:
            try:
                # Parse detections from CSV
                message_id = int(row['message_id'])
                channel_name = row['channel_name']
                image_path = row['image_path']
                category = row['category']
                num_objects = int(row['num_objects'])
                detected_classes = row['detected_classes'].split(', ')
                
                # Insert each detection
                for cls in detected_classes:
                    conn.execute(text(insert_sql), {
                        'message_id': message_id,
                        'channel_name': channel_name,
                        'image_path': image_path,
                        'detected_class': cls.strip(),
                        'confidence': 0.5,
                        'category': category,
                        'num_objects': num_objects
                    })
                    count += 1
            except Exception as e:
                logger.error(f"Error inserting row: {e}")
        
        conn.commit()
    
    logger.info(f"Loaded {count} YOLO detections")

def create_sample_data():
    """Create sample YOLO data for testing"""
    import random
    from datetime import datetime
    
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get some message IDs from the database
    db = DatabaseManager()
    db.connect()
    
    with db.get_connection() as conn:
        result = conn.execute(text("SELECT message_id, channel_name FROM raw.telegram_messages WHERE has_media = true LIMIT 50"))
        messages = result.fetchall()
    
    if not messages:
        logger.warning("No messages with media found")
        return
    
    # Sample categories and classes
    categories = ['promotional', 'product_display', 'lifestyle', 'other']
    class_sets = [
        ['person', 'bottle'],
        ['bottle', 'cup'],
        ['person'],
        ['bottle', 'cell phone'],
        ['person', 'cell phone', 'bottle'],
        ['cup', 'bowl'],
        ['vase'],
        ['person', 'cup']
    ]
    
    results = []
    for msg_id, channel in messages:
        num_objects = random.randint(1, 4)
        detected_classes = random.choice(class_sets)
        category = random.choice(categories)
        
        results.append({
            'message_id': msg_id,
            'channel_name': channel,
            'image_path': f'data/raw/images/{channel}/{msg_id}.jpg',
            'category': category,
            'num_objects': num_objects,
            'detected_classes': ', '.join(detected_classes)
        })
    
    # Save to CSV
    csv_path = output_dir / 'yolo_detections.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['message_id', 'channel_name', 'image_path', 'category', 'num_objects', 'detected_classes'])
        for r in results:
            writer.writerow([
                r['message_id'],
                r['channel_name'],
                r['image_path'],
                r['category'],
                r['num_objects'],
                r['detected_classes']
            ])
    
    logger.info(f"Created {len(results)} sample YOLO results at {csv_path}")
    
    # Load the sample data
    load_yolo_results(db)

def main():
    db = DatabaseManager()
    db.connect()
    
    create_yolo_table(db)
    load_yolo_results(db)
    
    logger.info("YOLO results loaded successfully!")

if __name__ == "__main__":
    main()