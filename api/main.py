"""
FastAPI application for the Medical Telegram Warehouse.
Provides analytical endpoints for querying the data warehouse.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import logging

from sqlalchemy import text
from pydantic import BaseModel

# Add parent directory to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical Telegram Warehouse API",
    description="Analytical API for Ethiopian medical business Telegram data",
    version="1.0.0"
)

# Initialize database connection
db = DatabaseManager()
db.connect()

# Pydantic models for responses
class TopProduct(BaseModel):
    product_term: str
    mention_count: int
    
class ChannelActivity(BaseModel):
    date: str
    message_count: int
    avg_views: float
    avg_forwards: float
    
class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_date: str
    message_text: str
    views: int
    forwards: int
    has_image: bool
    
class VisualContentStats(BaseModel):
    channel_name: str
    total_images: int
    images_with_detections: int
    promotion_count: int
    product_display_count: int
    lifestyle_count: int
    other_count: int
    avg_views_promotional: Optional[float]
    avg_views_product_display: Optional[float]

# Helper function to extract product mentions (simplified)
def extract_product_terms(text: str) -> List[str]:
    """Extract potential product terms from message text."""
    # This is a simplified version - in production you'd use NLP
    # Common medical product terms in Ethiopian context
    common_terms = [
        'paracetamol', 'amoxicillin', 'ibuprofen', 'aspirin',
        'vitamin', 'cream', 'ointment', 'syrup', 'tablet',
        'capsule', 'injection', 'solution', 'gel', 'lotion'
    ]
    terms = []
    text_lower = text.lower()
    for term in common_terms:
        if term in text_lower:
            terms.append(term)
    return terms

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medical Telegram Warehouse API",
        "docs": "/docs",
        "endpoints": [
            "/api/reports/top-products",
            "/api/channels/{channel_name}/activity",
            "/api/search/messages",
            "/api/reports/visual-content"
        ]
    }

@app.get("/api/reports/top-products", response_model=List[TopProduct])
async def get_top_products(limit: int = Query(10, ge=1, le=50)):
    """
    Get the most frequently mentioned products across all channels.
    
    Args:
        limit: Number of products to return (1-50)
    """
    try:
        # Query to get product mentions from messages
        # This is a simplified version using text extraction
        query = """
        SELECT 
            message_text,
            COUNT(*) as mention_count
        FROM marts.fct_messages
        WHERE message_text IS NOT NULL
        GROUP BY message_text
        ORDER BY mention_count DESC
        LIMIT :limit
        """
        
        # For now, return sample data
        # In production, this would use proper text analysis
        sample_products = [
            TopProduct(product_term="Paracetamol", mention_count=45),
            TopProduct(product_term="Amoxicillin", mention_count=38),
            TopProduct(product_term="Vitamin C", mention_count=32),
            TopProduct(product_term="Ibuprofen", mention_count=28),
            TopProduct(product_term="Skin Cream", mention_count=25),
        ]
        
        return sample_products[:limit]
        
    except Exception as e:
        logger.error(f"Error getting top products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivity])
async def get_channel_activity(
    channel_name: str,
    days: int = Query(30, ge=1, le=90)
):
    """
    Get posting activity and trends for a specific channel.
    
    Args:
        channel_name: Name of the channel
        days: Number of days to analyze (1-90)
    """
    try:
        # Query to get daily activity
        # This would query the fct_messages table
        # For now, return sample data
        sample_data = []
        for i in range(days, 0, -1):
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date = date.replace(day=date.day - i)
            sample_data.append(
                ChannelActivity(
                    date=date.isoformat(),
                    message_count=5 + (i % 10),
                    avg_views=100 + (i * 3),
                    avg_forwards=10 + (i % 5)
                )
            )
        
        return sample_data
        
    except Exception as e:
        logger.error(f"Error getting channel activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/messages", response_model=List[MessageSearchResult])
async def search_messages(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for messages containing a specific keyword.
    
    Args:
        query: Search keyword
        limit: Maximum number of results to return (1-100)
    """
    try:
        # Query to search messages
        search_query = """
        SELECT 
            message_id,
            channel_name,
            message_date,
            message_text,
            views,
            forwards,
            has_image
        FROM marts.fct_messages
        WHERE message_text ILIKE :query
        ORDER BY message_date DESC
        LIMIT :limit
        """
        
        # For now, return sample data
        sample_messages = []
        for i in range(min(limit, 10)):
            sample_messages.append(
                MessageSearchResult(
                    message_id=1000 + i,
                    channel_name="CheMed",
                    message_date=datetime.now().isoformat(),
                    message_text=f"Sample message containing {query} #{i}",
                    views=50 + i * 10,
                    forwards=5 + i,
                    has_image=i % 2 == 0
                )
            )
        
        return sample_messages
        
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/visual-content", response_model=List[VisualContentStats])
async def get_visual_content_stats():
    """
    Get statistics about image usage across channels.
    """
    try:
        # Query to get visual content stats
        # This would join fct_messages with fct_image_detections
        # For now, return sample data
        sample_stats = [
            VisualContentStats(
                channel_name="CheMed",
                total_images=150,
                images_with_detections=120,
                promotion_count=45,
                product_display_count=50,
                lifestyle_count=15,
                other_count=10,
                avg_views_promotional=250.5,
                avg_views_product_display=180.3
            ),
            VisualContentStats(
                channel_name="LobeliaCosmetics",
                total_images=100,
                images_with_detections=85,
                promotion_count=30,
                product_display_count=35,
                lifestyle_count=12,
                other_count=8,
                avg_views_promotional=320.7,
                avg_views_product_display=195.2
            ),
            VisualContentStats(
                channel_name="TikvahPharma",
                total_images=80,
                images_with_detections=70,
                promotion_count=20,
                product_display_count=30,
                lifestyle_count=10,
                other_count=10,
                avg_views_promotional=180.2,
                avg_views_product_display=160.8
            )
        ]
        
        return sample_stats
        
    except Exception as e:
        logger.error(f"Error getting visual content stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}