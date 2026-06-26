"""
Download images from Telegram messages that have media
"""
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def download_images():
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    client = TelegramClient('image_downloader', api_id, api_hash)
    await client.start()
    
    logger.info("Connected to Telegram!")
    
    # Channels from your data
    channels = [
        'EHPMOFFICIAL',
        'EMA_Ethiopia',
        'epn_2025',
        'ethio_vital_health',
        'ethiomedicalgroup',
        'greatethiopharma',
        'lobelia4cosmetics',
        'PharmacyHubEthiopia'
    ]
    
    images_dir = Path('data/raw/images')
    images_dir.mkdir(parents=True, exist_ok=True)
    
    total_images = 0
    
    for channel_name in channels:
        try:
            logger.info(f"Checking @{channel_name} for images...")
            entity = await client.get_entity(f"@{channel_name}")
            
            # Create channel directory
            channel_dir = images_dir / channel_name
            channel_dir.mkdir(exist_ok=True)
            
            # Get messages with media
            count = 0
            async for message in client.iter_messages(entity, limit=200):
                if message.media and hasattr(message.media, 'photo'):
                    # Download the image
                    image_path = channel_dir / f"{message.id}.jpg"
                    if not image_path.exists():
                        await message.download_media(file=str(image_path))
                        count += 1
                        logger.info(f"  Downloaded: {channel_name}/{message.id}.jpg")
                        await asyncio.sleep(0.2)  # Small delay to avoid rate limiting
            
            total_images += count
            logger.info(f"Downloaded {count} images from @{channel_name}")
            
        except Exception as e:
            logger.error(f"Error with @{channel_name}: {e}")
    
    logger.info(f"Total images downloaded: {total_images}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(download_images())