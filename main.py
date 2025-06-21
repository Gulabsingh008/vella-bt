import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError, FloodWait
from datetime import datetime, timedelta

# ✅ Bot credentials (Environment Variables से लोड करें)
BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": int(os.getenv("BOT1_API_ID", "26494161")),
        "api_hash": os.getenv("BOT1_API_HASH", "55da841f877d16a3a806169f3c5153d3"),
        "bot_token": os.getenv("BOT1_TOKEN", "7670198611:AAEwf0-xqEiBHocibNAXMRqz08TIVFWz8PM")
    },
    {
        "name": "bot2",
        "api_id": int(os.getenv("BOT2_API_ID", "24519654")),
        "api_hash": os.getenv("BOT2_API_HASH", "1ccea9c29a420df6a6622383fbd83bcd"),
        "bot_token": os.getenv("BOT2_TOKEN", "7982548340:AAHEfCDzWEKMb6h6EBdwNaG1VzSvIhrMk7I")
    },
    {
        "name": "control_bot",
        "api_id": int(os.getenv("CONTROL_API_ID", "26494161")),
        "api_hash": os.getenv("CONTROL_API_HASH", "55da841f877d16a3a806169f3c5153d3"),
        "bot_token": os.getenv("CONTROL_BOT_TOKEN", "7785044097:AAHmF3GsTj49jfKqrjczS2xOTUQ52NPKlP0")
    }
]

# ✅ Channel IDs (Environment Variables से लोड करें)
RAW_CHAT_IDS = [int(id) if id.lstrip('-').isdigit() else id.strip() 
               for id in os.getenv("CHAT_IDS", "-1002246848988").split(",")]

# ✅ Admin user IDs (Environment Variables से लोड करें)
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "1114789110").split(",") if id]

# ✅ General settings (Environment Variables से लोड करें)
SPAM_INTERVAL = int(os.getenv("SPAM_INTERVAL", "3600"))  # seconds
AUTO_SPAM = os.getenv("AUTO_SPAM", "True").lower() == "true"  # start with auto-spam on

# ✅ Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

class BotManager:
    def __init__(self):
        self.auto_spam = AUTO_SPAM
        self.spam_interval = SPAM_INTERVAL
        self.last_spam_time = {}
        self.admin_ids = ADMIN_IDS
        self.active_bots = []
        self.resolved_chat_ids = []

    async def initialize_bots(self):
        """सभी बॉट्स को इनिशियलाइज़ करें"""
        for config in BOTS_CONFIG:
            try:
                bot = Client(
                    name=config["name"],
                    api_id=config["api_id"],
                    api_hash=config["api_hash"],
                    bot_token=config["bot_token"],
                    in_memory=True
                )

                if config["name"] == "control_bot":
                    self._add_control_handlers(bot)
                else:
                    self._add_basic_handlers(bot)

                await bot.start()
                me = await bot.get_me()
                logger.info(f"✅ Started {config['name']} as @{me.username}")
                self.active_bots.append(bot)

            except Exception as e:
                logger.error(f"❌ Failed to start {config['name']}: {e}")
                raise

        await self.resolve_chat_ids()

    async def resolve_chat_ids(self):
        """चैट आईडी को रिजॉल्व करें और पर्मिशन चेक करें"""
        self.resolved_chat_ids = []
        if not self.active_bots:
            return

        bot = self.active_bots[0]  # पहले बॉट का उपयोग करें
        
        for raw_id in RAW_CHAT_IDS:
            try:
                # चैट जॉइन करने की कोशिश करें
                try:
                    await bot.join_chat(raw_id)
                    logger.info(f"Joined chat: {raw_id}")
                except Exception as join_error:
                    logger.warning(f"Couldn't join chat {raw_id}: {join_error}")

                # चैट डिटेल्स प्राप्त करें
                chat = await bot.get_chat(raw_id)
                
                # पर्मिशन चेक करें
                if hasattr(chat, 'permissions') and chat.permissions:
                    if not chat.permissions.can_send_messages:
                        logger.error(f"⚠️ No permission to send messages in {chat.title}")
                        continue
                
                self.resolved_chat_ids.append(chat.id)
                logger.info(f"✅ Resolved chat: {chat.title or chat.id} (ID: {chat.id})")

            except Exception as e:
                logger.error(f"❌ Failed to resolve chat {raw_id}: {str(e)}")

    def _add_basic_handlers(self, bot):
        """बेसिक कमांड हैंडलर्स जोड़ें"""
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"👋 Hello! I am @{client.me.username}")

    def _add_control_handlers(self, bot):
        """एडमिन कंट्रोल हैंडलर्स जोड़ें"""
        @bot.on_message(filters.command("spam_on") & filters.user(self.admin_ids))
        async def enable_spam(client, message):
            self.auto_spam = True
            await message.reply("✅ Spam mode turned ON")
            logger.info("Spam mode enabled by admin")

        @bot.on_message(filters.command("spam_off") & filters.user(self.admin_ids))
        async def disable_spam(client, message):
            self.auto_spam = False
            await message.reply("🛑 Spam mode turned OFF")
            logger.info("Spam mode disabled by admin")

    async def spam_channels(self):
        SPAM_MESSAGES = [
            "🔥 Follow करो चैनल!",
            "📢 आज की नई अपडेट देखें!",
            "📡 Tech, Jobs और Fun एक जगह!",
            "🎯 कंटेंट जो आपको Grow करे!",
            "🧠 Daily Knowledge Boost लो!"
        ]

        while True:
            if self.auto_spam and self.resolved_chat_ids:
                for bot in self.active_bots:
                    if "control" in bot.name:
                        continue
                        
                    for chat_id in self.resolved_chat_ids:
                        try:
                            # चैट में है या नहीं यह चेक करें
                            try:
                                await bot.get_chat(chat_id)
                            except:
                                logger.warning(f"Bot not in chat {chat_id}, trying to join...")
                                await bot.join_chat(chat_id)
                            
                            # मैसेज भेजें
                            for msg in SPAM_MESSAGES:
                                try:
                                    await bot.send_message(chat_id, msg)
                                    await asyncio.sleep(5)  # Anti-flood delay
                                except FloodWait as e:
                                    logger.warning(f"⏳ Flood wait {e.value}s")
                                    await asyncio.sleep(e.value)
                                except RPCError as e:
                                    logger.error(f"⚠️ Error sending to {chat_id}: {e}")
                                    break
                                    
                        except Exception as e:
                            logger.error(f"❌ Error processing chat {chat_id}: {e}")
                            
            await asyncio.sleep(60)

async def main():
    manager = BotManager()
    await manager.initialize_bots()
    asyncio.create_task(manager.spam_channels())
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
