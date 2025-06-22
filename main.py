import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import (ChatWriteForbiddenError, 
                           AccessTokenExpiredError,
                           RPCError)

load_dotenv()

BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": int(os.getenv("BOT1_API_ID", 0)),
        "api_hash": os.getenv("BOT1_API_HASH", ""),
        "bot_token": os.getenv("BOT1_TOKEN", ""),
        "log_channel": int(os.getenv("BOT1_LOG_CHANNEL", 0))
    },
    {
        "name": "bot2",
        "api_id": int(os.getenv("BOT2_API_ID", 0)),
        "api_hash": os.getenv("BOT2_API_HASH", ""),
        "bot_token": os.getenv("BOT2_TOKEN", ""),
        "log_channel": int(os.getenv("BOT2_LOG_CHANNEL", 0))
    }
]

async def create_bot_client(config):
    try:
        print(f"🚀 Starting {config['name']}...")
        client = TelegramClient(
            session=config['name'],
            api_id=config['api_id'],
            api_hash=config['api_hash']
        )
        
        await client.start(bot_token=config['bot_token'])
        
        @client.on(events.NewMessage(pattern="/start"))
        async def handle_start(event):
            # ... (keep your existing handler code)
        
        me = await client.get_me()
        print(f"✅ {config['name']} started as @{me.username}")
        return client
        
    except AccessTokenExpiredError:
        print(f"❌ {config['name']}: Bot token expired or invalid")
        raise
    except RPCError as e:
        print(f"❌ {config['name']}: Connection failed - {e}")
        raise
    except Exception as e:
        print(f"❌ {config['name']}: Unexpected error - {e}")
        raise

async def main():
    try:
        clients = await asyncio.gather(
            *(create_bot_client(cfg) for cfg in BOTS_CONFIG),
            return_exceptions=True
        )
        
        # Filter out failed clients
        active_clients = [c for c in clients if isinstance(c, TelegramClient)]
        
        if not active_clients:
            print("❌ No bots started successfully")
            return
            
        print("⚙️ Bots running. Press Ctrl+C to stop")
        await asyncio.gather(*(client.run_until_disconnected() for client in active_clients))
        
    except KeyboardInterrupt:
        print("🛑 Stopping bots...")
    finally:
        print("🧹 Cleaning up...")
        await asyncio.gather(*(c.disconnect() for c in active_clients if hasattr(c, 'disconnect')))
        print("👋 All bots stopped")

if __name__ == "__main__":
    asyncio.run(main())
