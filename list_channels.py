"""
List all channels you're a member of
"""
import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Get API credentials from environment variables
    api_id_str = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    # Check if credentials exist
    if not api_id_str or not api_hash:
        print("❌ Error: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env file")
        return
    
    api_id = int(api_id_str)
    
    client = TelegramClient('list_session', api_id, api_hash)
    await client.start()
    
    print("✅ Connected to Telegram!")
    print("\n📋 Your channels and groups:\n")
    print("=" * 70)
    
    count = 0
    medical_channels = []
    other_channels = []
    
    async for dialog in client.iter_dialogs():
        if dialog.is_channel or dialog.is_group:
            count += 1
            name = dialog.name
            username = f"@{dialog.entity.username}" if dialog.entity.username else "No username"
            
            # Check if it's medical-related
            medical_keywords = ['medical', 'pharma', 'health', 'drug', 'chem', 'clinic', 
                              'doctor', 'pharmacy', 'med', 'care', 'drugs', 'supplement',
                              'hospital', 'nurse', 'treatment', 'medicine', 'wellness']
            is_medical = any(term in name.lower() for term in medical_keywords)
            
            if is_medical:
                medical_channels.append((name, username))
            else:
                other_channels.append((name, username))
    
    # Print medical channels first
    print("🩺 MEDICAL-RELATED CHANNELS:")
    print("-" * 70)
    for idx, (name, username) in enumerate(medical_channels, 1):
        print(f"{idx:3}. {name} - {username}")
    
    print("\n📢 OTHER CHANNELS:")
    print("-" * 70)
    for idx, (name, username) in enumerate(other_channels, 1):
        print(f"{idx:3}. {name} - {username}")
    
    print("=" * 70)
    print(f"\n📊 Total: {count} channels/groups")
    print(f"🩺 Medical-related: {len(medical_channels)}")
    print(f"📢 Other: {len(other_channels)}")
    print("\n💡 Tip: Look at the medical channels and note their usernames")
    print("   Then update src/scraper.py with these usernames.")
    
    await client.disconnect()
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())