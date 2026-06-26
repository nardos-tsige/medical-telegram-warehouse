"""
YOLO object detection for Telegram images.
Detects objects in images and categorizes them for analytical purposes.
"""
import os
import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ultralytics import YOLO
from PIL import Image
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/yolo_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YOLODetector:
    """
    YOLO object detection for Telegram images.
    """
    
    # Classification scheme for images
    IMAGE_CATEGORIES = {
        'promotional': ['person', 'cell phone', 'bottle'],
        'product_display': ['bottle', 'cup', 'bowl', 'vase'],
        'lifestyle': ['person'],
        'other': []
    }
    
    def __init__(self, model_name: str = 'yolov8n.pt'):
        """
        Initialize YOLO detector.
        
        Args:
            model_name: YOLO model to use (default: yolov8n.pt for efficiency)
        """
        self.model = YOLO(model_name)
        self.images_dir = Path('data/raw/images')
        self.output_dir = Path('data/processed')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
        logger.info(f"YOLO Detector initialized with model: {model_name}")
        
    def scan_images(self) -> List[Path]:
        """
        Scan for images in the data directory.
        
        Returns:
            List of image paths
        """
        image_paths = []
        
        if not self.images_dir.exists():
            logger.warning(f"Images directory {self.images_dir} does not exist")
            return image_paths
            
        # Walk through all subdirectories
        for channel_dir in self.images_dir.iterdir():
            if not channel_dir.is_dir():
                continue
                
            for image_file in channel_dir.glob('*.jpg'):
                image_paths.append(image_file)
                
        logger.info(f"Found {len(image_paths)} images to process")
        return image_paths
        
    def detect_objects(self, image_path: Path) -> Dict[str, Any]:
        """
        Run object detection on a single image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Run inference
            results = self.model(image_path)
            
            # Extract detections
            detections = []
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = self.model.names[cls]
                        detections.append({
                            'class': class_name,
                            'confidence': conf
                        })
            
            # Categorize the image
            category = self.categorize_image(detections)
            
            # Extract message_id from filename
            message_id = int(image_path.stem)
            channel_name = image_path.parent.name
            
            result = {
                'message_id': message_id,
                'channel_name': channel_name,
                'image_path': str(image_path),
                'detections': detections,
                'category': category,
                'num_objects': len(detections),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting objects in {image_path}: {e}")
            return None
            
    def categorize_image(self, detections: List[Dict[str, Any]]) -> str:
        """
        Categorize an image based on detected objects.
        
        Args:
            detections: List of detected objects
            
        Returns:
            Category string: 'promotional', 'product_display', 'lifestyle', or 'other'
        """
        detected_classes = [d['class'] for d in detections]
        
        # Check for promotional (person + product)
        if 'person' in detected_classes:
            has_product = any(
                cls in ['bottle', 'cup', 'bowl', 'vase', 'cell phone']
                for cls in detected_classes
            )
            if has_product:
                return 'promotional'
            else:
                return 'lifestyle'
                
        # Check for product display
        has_product = any(
            cls in ['bottle', 'cup', 'bowl', 'vase']
            for cls in detected_classes
        )
        if has_product:
            return 'product_display'
            
        return 'other'
        
    def process_all_images(self) -> List[Dict[str, Any]]:
        """
        Process all images in the data directory.
        
        Returns:
            List of detection results
        """
        image_paths = self.scan_images()
        results = []
        
        for idx, image_path in enumerate(image_paths):
            logger.info(f"Processing image {idx + 1}/{len(image_paths)}: {image_path}")
            
            result = self.detect_objects(image_path)
            if result:
                results.append(result)
                
            # Log progress every 10 images
            if (idx + 1) % 10 == 0:
                logger.info(f"Processed {idx + 1} images so far")
                
        self.results = results
        
        # Save results
        self.save_results()
        
        logger.info(f"Completed detection on {len(results)} images")
        return results
        
    def save_results(self):
        """Save detection results to CSV and JSON."""
        if not self.results:
            logger.warning("No results to save")
            return
            
        # Save to CSV
        csv_path = self.output_dir / 'yolo_detections.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'message_id', 'channel_name', 'image_path', 
                'category', 'num_objects', 'detected_classes', 
                'timestamp'
            ])
            
            for result in self.results:
                detected_classes = [d['class'] for d in result['detections']]
                writer.writerow([
                    result['message_id'],
                    result['channel_name'],
                    result['image_path'],
                    result['category'],
                    result['num_objects'],
                    ', '.join(detected_classes),
                    result['timestamp']
                ])
                
        logger.info(f"Results saved to {csv_path}")
        
        # Also save as JSON with full details
        json_path = self.output_dir / 'yolo_detections.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        logger.info(f"Results saved to {json_path}")
        
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of detection results.
        
        Returns:
            Summary dictionary
        """
        if not self.results:
            return {'error': 'No results available'}
            
        df = pd.DataFrame(self.results)
        
        summary = {
            'total_images_processed': len(self.results),
            'category_distribution': df['category'].value_counts().to_dict(),
            'channels': df['channel_name'].value_counts().to_dict(),
            'avg_objects_per_image': df['num_objects'].mean(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save summary
        summary_path = self.output_dir / 'yolo_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"Summary saved to {summary_path}")
        return summary

def main():
    """Main entry point for YOLO detection."""
    detector = YOLODetector()
    results = detector.process_all_images()
    summary = detector.generate_summary()
    
    print("\n" + "="*50)
    print("YOLO Detection Summary")
    print("="*50)
    print(f"Total images processed: {summary['total_images_processed']}")
    print(f"Category distribution: {summary['category_distribution']}")
    print("="*50)

if __name__ == "__main__":
    main()