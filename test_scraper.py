"""
Test script to find and scrape medical channels in Ethiopia
"""
import asyncio
import os
from datetime import datetime, timedelta
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
        print("Please check your .env file and try again.")
        return
    
    api_id = int(api_id_str)
    
    client = TelegramClient('test_session', api_id, api_hash)
    await client.start()
    
    print("✅ Connected to Telegram!")
    print("\n🔍 Searching for Ethiopian medical channels...")
    
    # List of potential channel names to try
    channels_to_try = [
        'CheMed', 'chemed', 'CheMedEthiopia',
        'LobeliaCosmetics', 'lobeliacosmetics',
        'TikvahPharma', 'tikvahpharma',
        'EthioPharma', 'EthiopianPharmacy',
        'AddisMedical', 'EthioHealth',
        'PharmaET', 'MedEthiopia',
        'ethiopian_pharmacy', 'addis_pharma',
        'ethio_medical', 'addis_medical',
        'pharma_ethiopia', 'health_ethiopia'
    ]
    
    found_channels = []
    
    for channel_name in channels_to_try:
        try:
            entity = await client.get_entity(f'@{channel_name}')
            found_channels.append({
                'username': channel_name,
                'title': entity.title,
                'id': entity.id
            })
            print(f"✅ Found: @{channel_name} -> {entity.title}")
        except Exception:
            print(f"❌ Not found: @{channel_name}")
    
    if found_channels:
        print(f"\n✅ Found {len(found_channels)} channels!")
        
        # Scrape the first found channel
        channel_info = found_channels[0]
        print(f"\n📊 Scraping {channel_info['title']} (@{channel_info['username']})...")
        print("-" * 50)
        
        entity = await client.get_entity(f"@{channel_info['username']}")
        
        # Get recent messages (last 7 days)
        start_date = datetime.now() - timedelta(days=7)
        message_count = 0
        messages = []
        
        async for message in client.iter_messages(entity, limit=50):
            if message.date.replace(tzinfo=None) < start_date:
                break
            message_count += 1
            if message_count <= 5:
                text_preview = message.text[:50] if message.text else '[No text]'
                messages.append(f"📝 Message {message_count}: {text_preview}...")
                print(messages[-1])
        
        print("-" * 50)
        print(f"\n📊 Total messages in last 7 days: {message_count}")
        
        # Show channel info
        print(f"\n📌 Channel: {channel_info['title']}")
        print(f"🔗 Username: @{channel_info['username']}")
        print(f"🆔 ID: {channel_info['id']}")
        
    else:
        print("\n❌ No channels found.")
        print("\n📌 Suggestions:")
        print("1. Open Telegram app on your phone")
        print("2. Search for 'Ethiopian pharmacy' or 'medical Ethiopia'")
        print("3. Find channels that interest you")
        print("4. Note their @username")
        print("5. Update the channels_to_try list above")
    
    await client.disconnect()
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())