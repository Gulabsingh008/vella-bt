import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import ChatWriteForbiddenError, AccessTokenExpiredError

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
    },
    {
        "name": "bot3",
        "api_id": int(os.getenv("BOT3_API_ID")),
        "api_hash": os.getenv("BOT3_API_HASH"),
        "bot_token": os.getenv("BOT3_TOKEN"),
        "log_channel": int(os.getenv("BOT3_LOG_CHANNEL"))
    },
    {
        "name": "bot4",
        "api_id": int(os.getenv("BOT4_API_ID")),
        "api_hash": os.getenv("BOT4_API_HASH"),
        "bot_token": os.getenv("BOT4_TOKEN"),
        "log_channel": int(os.getenv("BOT4_LOG_CHANNEL"))
    },
    {
        "name": "bot5",
        "api_id": int(os.getenv("BOT5_API_ID")),
        "api_hash": os.getenv("BOT5_API_HASH"),
        "bot_token": os.getenv("BOT5_TOKEN"),
        "log_channel": int(os.getenv("BOT5_LOG_CHANNEL"))
    },
    {
        "name": "bot6",
        "api_id": int(os.getenv("BOT6_API_ID")),
        "api_hash": os.getenv("BOT6_API_HASH"),
        "bot_token": os.getenv("BOT6_TOKEN"),
        "log_channel": int(os.getenv("BOT6_LOG_CHANNEL"))
    },
    {
        "name": "bot7",
        "api_id": int(os.getenv("BOT7_API_ID")),
        "api_hash": os.getenv("BOT7_API_HASH"),
        "bot_token": os.getenv("BOT7_TOKEN"),
        "log_channel": int(os.getenv("BOT7_LOG_CHANNEL"))
    },
    {
        "name": "bot8",
        "api_id": int(os.getenv("BOT8_API_ID")),
        "api_hash": os.getenv("BOT8_API_HASH"),
        "bot_token": os.getenv("BOT8_TOKEN"),
        "log_channel": int(os.getenv("BOT8_LOG_CHANNEL"))
    },
    {
        "name": "bot9",
        "api_id": int(os.getenv("BOT9_API_ID")),
        "api_hash": os.getenv("BOT9_API_HASH"),
        "bot_token": os.getenv("BOT9_TOKEN"),
        "log_channel": int(os.getenv("BOT9_LOG_CHANNEL"))
    },
    {
        "name": "bot10",
        "api_id": int(os.getenv("BOT10_API_ID")),
        "api_hash": os.getenv("BOT10_API_HASH"),
        "bot_token": os.getenv("BOT10_TOKEN"),
        "log_channel": int(os.getenv("BOT10_LOG_CHANNEL"))
    },
    {
        "name": "bot11",
        "api_id": int(os.getenv("BOT11_API_ID")),
        "api_hash": os.getenv("BOT11_API_HASH"),
        "bot_token": os.getenv("BOT11_TOKEN"),
        "log_channel": int(os.getenv("BOT11_LOG_CHANNEL"))
    },
    {
        "name": "bot12",
        "api_id": int(os.getenv("BOT12_API_ID")),
        "api_hash": os.getenv("BOT12_API_HASH"),
        "bot_token": os.getenv("BOT12_TOKEN"),
        "log_channel": int(os.getenv("BOT12_LOG_CHANNEL"))
    },
    {
        "name": "bot13",
        "api_id": int(os.getenv("BOT13_API_ID")),
        "api_hash": os.getenv("BOT13_API_HASH"),
        "bot_token": os.getenv("BOT13_TOKEN"),
        "log_channel": int(os.getenv("BOT13_LOG_CHANNEL"))
    },
    {
        "name": "bot14",
        "api_id": int(os.getenv("BOT14_API_ID")),
        "api_hash": os.getenv("BOT14_API_HASH"),
        "bot_token": os.getenv("BOT14_TOKEN"),
        "log_channel": int(os.getenv("BOT14_LOG_CHANNEL"))
    },
    {
        "name": "bot15",
        "api_id": int(os.getenv("BOT15_API_ID")),
        "api_hash": os.getenv("BOT15_API_HASH"),
        "bot_token": os.getenv("BOT15_TOKEN"),
        "log_channel": int(os.getenv("BOT15_LOG_CHANNEL"))
    },
    {
        "name": "bot16",
        "api_id": int(os.getenv("BOT16_API_ID")),
        "api_hash": os.getenv("BOT16_API_HASH"),
        "bot_token": os.getenv("BOT16_TOKEN"),
        "log_channel": int(os.getenv("BOT16_LOG_CHANNEL"))
    },
    {
        "name": "bot17",
        "api_id": int(os.getenv("BOT17_API_ID")),
        "api_hash": os.getenv("BOT17_API_HASH"),
        "bot_token": os.getenv("BOT17_TOKEN"),
        "log_channel": int(os.getenv("BOT17_LOG_CHANNEL"))
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
            sender = await event.get_sender()
            user_mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            
            # 1st message
            await event.reply("👋 Hello! Welcome to the bot.")
            
            # 2nd message
            await asyncio.sleep(0.5)
            await event.reply("🎬 Uploading features are active.")
            
            # 3rd message
            await asyncio.sleep(0.5)
            await event.reply("📥 You can start using the service now.")
            
            # ❌ Log channel message removed (as per your request)
            # If needed later, you can re-enable below code
            """
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
            """


        me = await client.get_me()
        print(f"✅ {config['name']} started as @{me.username}")

        # 🔔 STARTUP LOG CHANNEL MESSAGE
        # inside create_bot_client() after `await client.get_me()` and print
        try:
            custom_msg = (
                "🎬 Title : Panchayat S04 2025 uploaded\n"
                "📤 Uploaded By: @Jk_Files\n\n"
                "Download link here\n\n"
                "https://t.me/+I7AR5Pf-KHQ0MzU1\n"
                "https://t.me/+I7AR5Pf-KHQ0MzU1\n"
                "https://t.me/+I7AR5Pf-KHQ0MzU1\n\n"
                "Also Join My New Backup Channel - \n"
                "https://t.me/+gUEnTgRaqD80MGNl\n"
                "https://t.me/+gUEnTgRaqD80MGNl\n"
            )
            await client.send_message(config['log_channel'], custom_msg)
            print(f"📩 Custom startup message sent for {config['name']}")
        except Exception as e:
            print(f"⚠️ Could not send custom startup log for {config['name']}: {e}")

        
        return client

    except Exception as e:
        print(f"❌ Failed to start {config['name']}: {e}")
        raise

async def main():
    clients = []
    try:
        clients = await asyncio.gather(
            *(create_bot_client(cfg) for cfg in BOTS_CONFIG),
            return_exceptions=True
        )

        active_clients = [c for c in clients if not isinstance(c, Exception)]

        if not active_clients:
            print("❌ No bots started successfully")
            return

        print("⚙️ Bots running. Press Ctrl+C to stop")
        await asyncio.gather(*(client.run_until_disconnected() for client in active_clients))

    except KeyboardInterrupt:
        print("🛑 Stopping bots...")
    finally:
        print("🧹 Cleaning up...")
        await asyncio.gather(*(c.disconnect() for c in clients if isinstance(c, TelegramClient)))
        print("👋 All bots stopped")

if __name__ == "__main__":
    asyncio.run(main())
