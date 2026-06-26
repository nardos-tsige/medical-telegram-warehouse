"""
Dagster pipeline for Medical Telegram Warehouse
"""
from dagster import (
    op,
    job,
    Definitions,
    ScheduleDefinition,
)
from datetime import datetime, timedelta
import subprocess
import sys
import os

@op
def scrape_telegram_data(context):
    """Scrape data from Telegram channels"""
    context.log.info("Starting Telegram scraper...")
    
    result = subprocess.run(
        [sys.executable, "src/scraper.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        context.log.error(f"Scraper failed: {result.stderr}")
        raise Exception(f"Scraper failed: {result.stderr}")
    
    context.log.info("Scraping completed successfully")
    return {"status": "success", "timestamp": datetime.now().isoformat()}

@op
def load_raw_data(context, scrape_result):
    """Load raw JSON data to PostgreSQL"""
    context.log.info("Loading raw data to PostgreSQL...")
    
    result = subprocess.run(
        [sys.executable, "scripts/load_raw_data.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        context.log.error(f"Load failed: {result.stderr}")
        raise Exception(f"Load failed: {result.stderr}")
    
    context.log.info("Data loaded successfully")
    return {"status": "success", "timestamp": datetime.now().isoformat()}

@op
def run_dbt_transformations(context, load_result):
    """Run dbt transformations"""
    context.log.info("Running dbt transformations...")
    
    result = subprocess.run(
        ["dbt", "run", "--project-dir", "medical_warehouse"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        context.log.error(f"dbt run failed: {result.stderr}")
        raise Exception(f"dbt run failed: {result.stderr}")
    
    context.log.info("dbt transformations completed")
    return {"status": "success", "timestamp": datetime.now().isoformat()}

@op
def run_yolo_enrichment(context, dbt_result):
    """Run YOLO object detection on images"""
    context.log.info("Running YOLO object detection...")
    
    images_dir = "data/raw/images"
    if not os.path.exists(images_dir):
        context.log.warning("No images found, skipping YOLO")
        return {"status": "skipped", "reason": "No images found"}
    
    result = subprocess.run(
        [sys.executable, "src/yolo_detect.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        context.log.error(f"YOLO failed: {result.stderr}")
        raise Exception(f"YOLO failed: {result.stderr}")
    
    context.log.info("YOLO detection completed")
    return {"status": "success", "timestamp": datetime.now().isoformat()}

@op
def load_yolo_results(context, yolo_result):
    """Load YOLO results to PostgreSQL"""
    context.log.info("Loading YOLO results to PostgreSQL...")
    
    if yolo_result.get("status") == "skipped":
        context.log.info("Skipping YOLO results load")
        return {"status": "skipped"}
    
    result = subprocess.run(
        [sys.executable, "scripts/load_yolo_results.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        context.log.error(f"Load YOLO results failed: {result.stderr}")
        raise Exception(f"Load YOLO results failed: {result.stderr}")
    
    context.log.info("YOLO results loaded successfully")
    return {"status": "success", "timestamp": datetime.now().isoformat()}

@job
def medical_warehouse_pipeline():
    """Full ETL pipeline for medical telegram warehouse"""
    scrape = scrape_telegram_data()
    load = load_raw_data(scrape)
    dbt = run_dbt_transformations(load)
    yolo = run_yolo_enrichment(dbt)
    load_yolo_results(yolo)

# Create a schedule that runs daily at 9 AM
daily_schedule = ScheduleDefinition(
    job=medical_warehouse_pipeline,
    cron_schedule="0 9 * * *",  # Runs at 9:00 AM every day
)

defs = Definitions(
    jobs=[medical_warehouse_pipeline],
    schedules=[daily_schedule],
)