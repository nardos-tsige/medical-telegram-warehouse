"""
Telegram scraper for Ethiopian medical business channels.
Extracts messages, images, and metadata from public Telegram channels.
"""
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from telethon import TelegramClient
from telethon.tl.types import Message, MessageMediaPhoto
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramScraper:
    """
    Scraper for Telegram channels focused on Ethiopian medical businesses.
    """
    
    TARGET_CHANNELS = [
        # Medical/Pharmacy channels
        'epn_2025',              # Ethiopian Pharmacy Network
        'ECPPN',                 # Ethiopian Clinical Pharmacy Professionals
        'EHPMOFFICIAL',          # Ethiopian Health Professionals' Movement
        'EMA_Ethiopia',          # Ethiopian Medical Association
        'MedicalSolution_Ethiopia', # Medical Solution Ethiopia
        'PharmacyHubEthiopia',   # Pharmacy Hub Ethiopia
        'STARSPHARMACYAA',       # Stars Pharmacy Addis Ababa
        'TIKVAHh',               # TIKVAH Pharmacy and health care
        'lobelia4cosmetics',     # Lobelia pharmacy and cosmetics
        'lobeliapharmacy',       # Lobelia Pharmacy and cosmetics
        'ethiopiaonlinepharmacy', # Online Pharmacy
        'greatethiopharma',      # Ethiopian pharmacy products
        'haltonspharmacyethiopia', # Haltons Pharmacy Ethiopia
        'ethiomedicalgroup',     # Ethiopia Medical Device Group
        'ethio_vital_health',    # Ethio Vital Health
    ]
    
    def __init__(self):
        """Initialize the Telegram scraper with API credentials."""
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if not self.api_id or not self.api_hash:
            raise ValueError(
                "TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env"
            )
        
        self.client = TelegramClient(
            'telegram_session',
            int(self.api_id),
            self.api_hash
        )
        
        # Data directories
        self.data_dir = Path('data/raw/telegram_messages')
        self.images_dir = Path('data/raw/images')
        self.logs_dir = Path('logs')
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.scraped_channels = set()
        
    async def start(self):
        """Start the Telegram client."""
        await self.client.start()
        logger.info("Telegram client started successfully")
        
    async def close(self):
        """Close the Telegram client."""
        await self.client.disconnect()
        logger.info("Telegram client disconnected")
        
    async def get_channel_entity(self, channel_name: str):
        """Get channel entity by username."""
        try:
            entity = await self.client.get_entity(f"@{channel_name}")
            return entity
        except Exception as e:
            logger.error(f"Failed to get channel @{channel_name}: {e}")
            return None
            
    async def scrape_channel(
        self,
        channel_name: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Scrape messages from a specific channel.
        
        Args:
            channel_name: The channel username (without @)
            days_back: Number of days of history to scrape
            
        Returns:
            List of message dictionaries
        """
        messages_data = []
        
        try:
            entity = await self.get_channel_entity(channel_name)
            if not entity:
                return messages_data
                
            # Calculate the date range - make dates naive (no timezone)
            end_date = datetime.now().replace(tzinfo=None)
            start_date = end_date - timedelta(days=days_back)
            
            logger.info(f"Scraping @{channel_name} from {start_date} to {end_date}")
            
            # Get messages from the channel
            async for message in self.client.iter_messages(
                entity,
                offset_date=end_date,
                reverse=False
            ):
                # Convert message date to naive for comparison
                message_date = message.date.replace(tzinfo=None)
                
                # Stop if we've reached the start date
                if message_date < start_date:
                    break
                    
                # Extract message data
                msg_data = self._extract_message_data(message, channel_name)
                
                # Download image if present
                if message.media and isinstance(message.media, MessageMediaPhoto):
                    image_path = await self._download_image(
                        message,
                        channel_name,
                        message.id
                    )
                    msg_data['image_path'] = image_path
                    msg_data['has_media'] = True
                
                messages_data.append(msg_data)
                
                # Log progress
                if len(messages_data) % 10 == 0:
                    logger.info(
                        f"Scraped {len(messages_data)} messages from @{channel_name}"
                    )
                    
            logger.info(
                f"Completed scraping @{channel_name}: {len(messages_data)} messages"
            )
            
            # Save messages to JSON
            if messages_data:
                self._save_messages(channel_name, messages_data)
                
            return messages_data
            
        except Exception as e:
            logger.error(f"Error scraping @{channel_name}: {e}")
            return messages_data
            
    def _extract_message_data(
        self,
        message: Message,
        channel_name: str
    ) -> Dict[str, Any]:
        """Extract relevant data from a Telegram message."""
        return {
            'message_id': message.id,
            'channel_name': channel_name,
            'message_date': message.date.isoformat(),
            'message_text': message.text or '',
            'has_media': bool(message.media),
            'image_path': None,
            'views': getattr(message, 'views', 0),
            'forwards': getattr(message, 'forwards', 0),
            'raw_data': {
                'id': message.id,
                'date': message.date.isoformat(),
                'text': message.text,
                'media': bool(message.media),
                'views': getattr(message, 'views', 0),
                'forwards': getattr(message, 'forwards', 0),
            }
        }
        
    async def _download_image(
        self,
        message: Message,
        channel_name: str,
        message_id: int
    ) -> Optional[str]:
        """
        Download image from a message.
        
        Args:
            message: The Telegram message
            channel_name: The channel name
            message_id: The message ID
            
        Returns:
            Path to the downloaded image or None if failed
        """
        try:
            # Create channel directory
            channel_dir = self.images_dir / channel_name
            channel_dir.mkdir(exist_ok=True)
            
            # Create image path
            image_path = channel_dir / f"{message_id}.jpg"
            
            # Download the image
            path = await message.download_media(file=str(image_path))
            
            if path:
                logger.info(f"Downloaded image to {path}")
                return str(image_path)
            else:
                logger.warning(f"Failed to download image for message {message_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading image for message {message_id}: {e}")
            return None
            
    def _save_messages(self, channel_name: str, messages: List[Dict[str, Any]]):
        """Save messages to a JSON file."""
        try:
            # Create date-based directory
            today = datetime.now().strftime('%Y-%m-%d')
            channel_dir = self.data_dir / today
            channel_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON
            file_path = channel_dir / f"{channel_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved {len(messages)} messages to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving messages for {channel_name}: {e}")
            
    async def scrape_all_channels(self, days_back: int = 30):
        """
        Scrape all configured channels.
        
        Args:
            days_back: Number of days of history to scrape
        """
        logger.info("Starting scrape of all channels")
        
        try:
            await self.start()
            
            for channel in self.TARGET_CHANNELS:
                try:
                    messages = await self.scrape_channel(channel, days_back)
                    if messages:
                        self.scraped_channels.add(channel)
                except Exception as e:
                    logger.error(f"Error scraping {channel}: {e}")
                    continue
                    
            logger.info(
                f"Scraping complete. Channels scraped: {self.scraped_channels}"
            )
            
            # Save scraping summary
            self._save_scraping_summary()
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        finally:
            await self.close()
            
    def _save_scraping_summary(self):
        """Save a summary of what was scraped."""
        summary_path = self.logs_dir / 'scraping_summary.json'
        summary = {
            'timestamp': datetime.now().isoformat(),
            'channels_scraped': list(self.scraped_channels),
            'total_channels': len(self.TARGET_CHANNELS),
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"Scraping summary saved to {summary_path}")

def main():
    """Main entry point for the scraper."""
    scraper = TelegramScraper()
    
    # Run the async scraper
    asyncio.run(scraper.scrape_all_channels(days_back=30))

if __name__ == "__main__":
    main()