"""
Unit tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_visual_content_endpoint():
    """Test visual content stats endpoint"""
    response = client.get("/api/reports/visual-content")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)