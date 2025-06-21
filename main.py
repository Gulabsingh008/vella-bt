import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError, FloodWait
from datetime import datetime, timedelta

# ✅ Bot credentials (HARDCODED)
BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": 26494161,
        "api_hash": "55da841f877d16a3a806169f3c5153d3",
        "bot_token": "7670198611:AAEwf0-xqEiBHocibNAXMRqz08TIVFWz8PM"
    },
    {
        "name": "bot2",
        "api_id": 24519654,
        "api_hash": "1ccea9c29a420df6a6622383fbd83bcd",
        "bot_token": "7982548340:AAHEfCDzWEKMb6h6EBdwNaG1VzSvIhrMk7I"
    },
    {
        "name": "control_bot",
        "api_id": 26494161,
        "api_hash": "55da841f877d16a3a806169f3c5153d3",
        "bot_token": "7785044097:AAHmF3GsTj49jfKqrjczS2xOTUQ52NPKlP0"
    }
]

# ✅ Channel IDs (can be numeric or usernames)
RAW_CHAT_IDS = [2246848988]  # You can also put "@channelusername"

# ✅ Admin user IDs (who can control spam via /spam_on or /spam_off)
ADMIN_IDS = [1114789110]

# ✅ General settings
SPAM_INTERVAL = 3600  # seconds
AUTO_SPAM = True  # start with auto-spam on

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

        # 🔁 Resolve chat IDs after all bots have started
        await self.auto_resolve_chat_ids()

    async def auto_resolve_chat_ids(self):
        """Auto resolve all chat IDs and store them."""
        self.resolved_chat_ids = []
        for bot in self.active_bots:
            if "control" in bot.name:
                continue
            for raw_id in RAW_CHAT_IDS:
                try:
                    chat = await bot.get_chat(raw_id)
                    self.resolved_chat_ids.append(chat.id)
                    logger.info(f"🔗 Resolved chat: {chat.title or chat.id}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not resolve chat ID {raw_id}: {e}")
            break  # Resolve only once using one bot

    def _add_basic_handlers(self, bot):
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"👋 Hello! I am @{client.me.username}.")

    def _add_control_handlers(self, bot):
        @bot.on_message(filters.command("spam_on") & filters.user(self.admin_ids))
        async def enable_spam(client, message):
            self.auto_spam = True
            await message.reply("✅ Spam mode turned ON.")

        @bot.on_message(filters.command("spam_off") & filters.user(self.admin_ids))
        async def disable_spam(client, message):
            self.auto_spam = False
            await message.reply("🛑 Spam mode turned OFF.")

    async def spam_channels(self):
        SPAM_MESSAGES = [
            "🔥 Follow करो चैनल!",
            "📢 आज की नई अपडेट देखें!",
            "📡 Tech, Jobs और Fun एक जगह!",
            "🎯 कंटेंट जो आपको Grow करे!",
            "🧠 Daily Knowledge Boost लो!"
        ]

        while True:
            if self.auto_spam:
                for bot in self.active_bots:
                    if "control" in bot.name:
                        continue
                    for chat_id in self.resolved_chat_ids:
                        key = (bot.name, chat_id)
                        last_time = self.last_spam_time.get(key, datetime.min)

                        if (datetime.now() - last_time) > timedelta(seconds=self.spam_interval):
                            for msg in SPAM_MESSAGES:
                                try:
                                    await bot.send_message(chat_id, msg)
                                    await asyncio.sleep(5)
                                except FloodWait as e:
                                    logger.warning(f"⏳ Flood wait {e.value}s: sleeping")
                                    await asyncio.sleep(e.value)
                                except RPCError as e:
                                    logger.warning(f"⚠️ {bot.name} → {chat_id}: {e}")
                            self.last_spam_time[key] = datetime.now()
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
        print("🛑 Bot stopped by user.")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
