"""
Search for Ethiopian medical channels on Telegram
"""
import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    client = TelegramClient('search_session', api_id, api_hash)
    await client.start()
    
    print("🔍 Searching for Ethiopian medical channels...\n")
    
    # Search queries
    queries = [
        'Ethiopian pharmacy',
        'Ethiopia medical',
        'Addis Ababa pharmacy',
        'Ethio health',
        'pharmacy Ethiopia',
        'medical Ethiopia',
        'drugs Ethiopia',
        'CheMed',
        'Lobelia',
        'Tikvah',
        'Ethiopian medicine',
        'healthcare Ethiopia'
    ]
    
    found_channels = set()
    
    for query in queries:
        print(f"\nSearching: '{query}'")
        print("-" * 50)
        
        try:
            # Search for channels
            result = await client(SearchRequest(
                q=query,
                limit=10
            ))
            
            for chat in result.chats:
                if hasattr(chat, 'username') and chat.username:
                    channel_name = chat.title if hasattr(chat, 'title') else chat.username
                    username = chat.username
                    
                    # Check if it might be Ethiopian
                    is_ethiopian = any(term in channel_name.lower() for term in ['ethio', 'addis', 'ethiopia', 'africa'])
                    if is_ethiopian or 'pharma' in channel_name.lower() or 'medical' in channel_name.lower():
                        key = f"@{username}"
                        if key not in found_channels:
                            found_channels.add(key)
                            print(f"✅ Found: {key} - {channel_name}")
        except Exception as e:
            print(f"Error searching '{query}': {e}")
    
    print("\n" + "="*50)
    print(f"Total channels found: {len(found_channels)}")
    print("\nAdd these to your scraper:")
    print("TARGET_CHANNELS = [")
    for channel in sorted(found_channels):
        print(f"    '{channel.lstrip('@')}',")
    print("]")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())