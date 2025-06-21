import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import RPCError

# 🔄 Environment Variables से क्रेडेंशियल्स लोड करें
def load_bots_from_env():
    bots = []
    i = 1
    while True:
        token = os.getenv(f"BOT{i}_TOKEN")
        if not token:
            break
            
        bots.append({
            "name": f"bot{i}",
            "api_id": int(os.getenv(f"BOT{i}_API_ID")),
            "api_hash": os.getenv(f"BOT{i}_API_HASH"),
            "bot_token": token
        })
        i += 1
    return bots

BOT_CREDENTIALS = load_bots_from_env()
AUTO_SPAM = os.getenv("AUTO_SPAM", "False").lower() == "true"

SPAM_MESSAGES = [
    "🔥 Follow our channel!",
    "📢 Check today's update!",
    "📡 Tech, Jobs and Fun in one place!",
    "🎯 Content that makes you Grow!",
    "🧠 Get Daily Knowledge Boost!"
]

async def spam_channels(bot):
    if not AUTO_SPAM:
        return
        
    try:
        async for dialog in bot.get_dialogs():
            if dialog.chat.type in ["channel", "supergroup"]:
                for msg in SPAM_MESSAGES:
                    try:
                        await bot.send_message(dialog.chat.id, msg)
                        await asyncio.sleep(5)  # Anti-spam delay
                    except RPCError as e:
                        print(f"⚠️ Error in {bot.name}: {e}")
    except Exception as e:
        print(f"❌ Fatal error in {bot.name}: {e}")

async def main():
    for cred in BOT_CREDENTIALS:
        try:
            bot = Client(
                name=cred["name"],
                api_id=cred["api_id"],
                api_hash=cred["api_hash"],
                bot_token=cred["bot_token"],
                in_memory=True  # Pyrogram v2+ के लिए जरूरी
            )
            
            @bot.on_message(filters.command("start"))
            async def start_handler(client, message):
                await message.reply(f"🤖 {client.me.username} is running!")
                
            await bot.start()
            print(f"✅ {cred['name']} started as @{(await bot.get_me()).username}")
            asyncio.create_task(spam_channels(bot))
            
        except Exception as e:
            print(f"❌ Failed to start {cred['name']}: {e}")

    await asyncio.Event().wait()  # बॉट्स को रनिंग रखें

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
