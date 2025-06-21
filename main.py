import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Bot Configuration (Multiple Bots + Log Channels)
BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": 26494161,
        "api_hash": "55da841f877d16a3a806169f3c5153d3",
        "bot_token": "7670198611:AAEwf0-xqEiBHocibNAXMRqz08TIVFWz8PM",
        "log_channel": -1002246848988  # Replace with your bot1 log channel ID
    },
    {
        "name": "bot2",
        "api_id": 24519654,
        "api_hash": "1ccea9c29a420df6a6622383fbd83bcd",
        "bot_token": "7982548340:AAHEfCDzWEKMb6h6EBdwNaG1VzSvIhrMk7I",
        "log_channel": -1002246848988  # Replace with your bot2 log channel ID
    }
]

clients = []

async def start_bot(config):
    app = Client(
        name=config["name"],
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        bot_token=config["bot_token"],
        in_memory=True
    )

    @app.on_message(filters.command("start"))
    async def handle_start(client: Client, message: Message):
        await message.reply_text(f"👋 Hello! I am @{(await client.get_me()).username}")

        log_text = f"👤 User: {message.from_user.mention}\n🆔 ID: {message.from_user.id}\n📥 Started the bot."
        try:
            await client.send_message(config["log_channel"], log_text)
        except Exception as e:
            print(f"❌ Failed to send log from {config['name']}: {e}")

    await app.start()
    print(f"✅ Started bot: {config['name']}")

    try:
        await app.send_message(config["log_channel"], "🤖 Bot Started! Stay tuned for updates.")
        print(f"📤 Log sent to channel: {config['log_channel']} (from {config['name']})")
    except Exception as e:
        print(f"⚠️ Failed to send startup log from {config['name']}: {e}")

    clients.append(app)

async def main():
    await asyncio.gather(*(start_bot(config) for config in BOTS_CONFIG))
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopping all bots...")
