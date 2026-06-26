"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TopProductResponse(BaseModel):
    """Response model for top products endpoint."""
    product_term: str = Field(..., description="Product or drug name")
    mention_count: int = Field(..., description="Number of times mentioned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_term": "Paracetamol",
                "mention_count": 45
            }
        }

class ChannelActivityResponse(BaseModel):
    """Response model for channel activity endpoint."""
    date: str = Field(..., description="Date of activity")
    message_count: int = Field(..., description="Number of messages posted")
    avg_views: float = Field(..., description="Average views per message")
    avg_forwards: float = Field(..., description="Average forwards per message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-06-25T00:00:00",
                "message_count": 12,
                "avg_views": 150.5,
                "avg_forwards": 15.3
            }
        }

class MessageSearchResponse(BaseModel):
    """Response model for message search endpoint."""
    message_id: int = Field(..., description="Unique message identifier")
    channel_name: str = Field(..., description="Channel name")
    message_date: str = Field(..., description="Message timestamp")
    message_text: str = Field(..., description="Message content")
    views: int = Field(..., description="Number of views")
    forwards: int = Field(..., description="Number of forwards")
    has_image: bool = Field(..., description="Whether message has an image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": 12345,
                "channel_name": "CheMed",
                "message_date": "2026-06-25T10:30:00",
                "message_text": "New shipment of Paracetamol arrived!",
                "views": 250,
                "forwards": 18,
                "has_image": True
            }
        }

class VisualContentStatsResponse(BaseModel):
    """Response model for visual content stats endpoint."""
    channel_name: str = Field(..., description="Channel name")
    total_images: int = Field(..., description="Total images in channel")
    images_with_detections: int = Field(..., description="Images with YOLO detections")
    promotion_count: int = Field(..., description="Promotional images count")
    product_display_count: int = Field(..., description="Product display count")
    lifestyle_count: int = Field(..., description="Lifestyle images count")
    other_count: int = Field(..., description="Other images count")
    avg_views_promotional: Optional[float] = Field(None, description="Avg views for promotional")
    avg_views_product_display: Optional[float] = Field(None, description="Avg views for product display")
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_name": "CheMed",
                "total_images": 150,
                "images_with_detections": 120,
                "promotion_count": 45,
                "product_display_count": 50,
                "lifestyle_count": 15,
                "other_count": 10,
                "avg_views_promotional": 250.5,
                "avg_views_product_display": 180.3
            }
        }

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Channel not found",
                "detail": "Channel 'InvalidChannel' does not exist"
            }
        }