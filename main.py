import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import ChatWriteForbiddenError

load_dotenv()

BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": int(os.getenv("BOT1_API_ID")),
        "api_hash": os.getenv("BOT1_API_HASH"),
        "bot_token": os.getenv("BOT1_TOKEN"),
        "log_channel": int(os.getenv("BOT1_LOG_CHANNEL"))
    },
    {
        "name": "bot2",
        "api_id": int(os.getenv("BOT2_API_ID")),
        "api_hash": os.getenv("BOT2_API_HASH"),
        "bot_token": os.getenv("BOT2_TOKEN"),
        "log_channel": int(os.getenv("BOT2_LOG_CHANNEL"))
    }
]

async def create_bot_client(config):
    client = TelegramClient(
        session=config['name'],
        api_id=config['api_id'],
        api_hash=config['api_hash']
    )
    
    # Start the client first
    await client.start(bot_token=config['bot_token'])
    
    @client.on(events.NewMessage(pattern="/start"))
    async def handle_start(event):
        sender = await event.get_sender()
        user_mention = f"[{sender.first_name}](tg://user?id={sender.id})"
        await event.reply(f"👋 Hello! I am @{(await client.get_me()).username}")

        log_msg = (
            f"👤 User: {user_mention}\n"
            f"🆔 ID: `{sender.id}`\n"
            f"📥 Started the bot."
        )

        try:
            await client.send_message(config['log_channel'], log_msg, parse_mode="md")
        except ChatWriteForbiddenError:
            print(f"⚠️ Bot has no permission to write to log channel: {config['log_channel']}")
        except Exception as e:
            print(f"❌ Log failed: {e}")

    me = await client.get_me()
    print(f"✅ {config['name']} started as @{me.username}")
    
    try:
        await client.send_message(config['log_channel'], f"✅ Bot @{me.username} Started. Stay tuned!")
        print(f"📩 Log channel message sent for {config['name']}")
    except Exception as e:
        print(f"⚠️ Failed to send startup log for {config['name']}: {e}")
    
    return client

async def main():
    clients = []
    try:
        # Create all bot clients first
        clients = await asyncio.gather(*(create_bot_client(cfg) for cfg in BOTS_CONFIG))
        print("⚙️ All bots started. Waiting for events...")
        
        # Keep the bots running
        await asyncio.gather(*(client.run_until_disconnected() for client in clients))
    finally:
        # Ensure proper cleanup
        await asyncio.gather(*(client.disconnect() for client in clients))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped.")
