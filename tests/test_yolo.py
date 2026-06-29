"""
Unit tests for YOLO detection module
"""
import pytest
import json
from pathlib import Path
from src.yolo_detect import YOLODetector

def test_yolo_initialization():
    """Test YOLO detector initialization"""
    detector = YOLODetector()
    assert detector.model is not None
    assert detector.images_dir == Path('data/raw/images')

def test_image_categorization():
    """Test image categorization logic"""
    detector = YOLODetector()
    
    # Test promotional detection
    detections = [{'class': 'person'}, {'class': 'bottle'}]
    category = detector.categorize_image(detections)
    assert category == 'promotional'
    
    # Test product display
    detections = [{'class': 'bottle'}, {'class': 'cup'}]
    category = detector.categorize_image(detections)
    assert category == 'product_display'
    
    # Test lifestyle
    detections = [{'class': 'person'}]
    category = detector.categorize_image(detections)
    assert category == 'lifestyle'
    
    # Test other
    detections = [{'class': 'car'}]
    category = detector.categorize_image(detections)
    assert category == 'other'

def test_results_file_created():
    """Test that YOLO results file is created"""
    detector = YOLODetector()
    results = detector.process_all_images()
    assert results is not None