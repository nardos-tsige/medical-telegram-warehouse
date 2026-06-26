"""
Test downloading images from one channel
"""
import os
import asyncio
import logging
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    client = TelegramClient('test_download', api_id, api_hash)
    await client.start()
    
    channel_name = 'lobelia4cosmetics'
    logger.info(f"Testing @{channel_name}...")
    
    try:
        entity = await client.get_entity(f"@{channel_name}")
        channel_dir = Path(f'data/raw/images/{channel_name}')
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        count = 0
        async for message in client.iter_messages(entity, limit=20):
            if message.media and hasattr(message.media, 'photo'):
                image_path = channel_dir / f"{message.id}.jpg"
                if not image_path.exists():
                    await message.download_media(file=str(image_path))
                    count += 1
                    logger.info(f"Downloaded: {message.id}.jpg")
        
        logger.info(f"Downloaded {count} images from @{channel_name}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())