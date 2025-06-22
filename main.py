import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors import ChatWriteForbiddenError

load_dotenv()  # Load environment variables

# Multiple Bot Configuration from environment variables
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

clients = []

async def start_bot(config):
    client = TelegramClient(
        session=config['name'],
        api_id=config['api_id'],
        api_hash=config['api_hash']
    ).start(bot_token=config['bot_token'])

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

    await client.start()
    me = await client.get_me()
    print(f"✅ {config['name']} started as @{me.username}")
    clients.append(client)

    try:
        await client.send_message(config['log_channel'], f"✅ Bot @{me.username} Started. Stay tuned!")
        print(f"📩 Log channel message sent for {config['name']}")
    except Exception as e:
        print(f"⚠️ Failed to send startup log for {config['name']}: {e}")

async def main():
    await asyncio.gather(*(start_bot(cfg) for cfg in BOTS_CONFIG))
    print("⚙️ All bots started. Waiting for events...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped.")
