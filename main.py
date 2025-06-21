import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from datetime import datetime, timedelta

# ✅ सभी बॉट्स के टोकन और API क्रेडेंशियल्स (hardcoded)
BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": 1111111,
        "api_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bot_token": "111111:ABC-bot1token"
    },
    {
        "name": "bot2",
        "api_id": 2222222,
        "api_hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "bot_token": "222222:DEF-bot2token"
    },
    {
        "name": "control_bot",
        "api_id": 3333333,
        "api_hash": "cccccccccccccccccccccccccccccccc",
        "bot_token": "333333:GHI-controlbottoken"
    }
]

# ✅ एडमिन IDs जो control commands चला सकते हैं
ADMIN_IDS = [123456789, 987654321]

# ✅ चैनल IDs जहाँ स्पैम भेजना है (manually added)
TARGET_CHAT_IDS = [
    -1001234567890,
    -1009876543210
]

# ✅ बाकी config
SPAM_INTERVAL = 3600  # seconds (1 hour default)
AUTO_SPAM = True  # चालू करते ही स्पैम शुरू हो जाए

# ✅ Log config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.auto_spam = AUTO_SPAM
        self.spam_interval = SPAM_INTERVAL
        self.last_spam_time = {}
        self.admin_ids = ADMIN_IDS
        self.active_bots = []

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
                logger.info(f"✅ {config['name']} started as @{me.username}")
                await bot.send_message("me", f"🤖 @{me.username} started successfully")
                self.active_bots.append(bot)

            except Exception as e:
                logger.error(f"❌ Failed to start {config['name']}: {e}")
                raise

    def _add_basic_handlers(self, bot):
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"🤖 Hello! I am {client.me.username}")

    def _add_control_handlers(self, bot):
        @bot.on_message(filters.command("spam_on") & filters.user(self.admin_ids))
        async def spam_on(client, message):
            self.auto_spam = True
            await message.reply("✅ Auto-spam mode turned ON")
            logger.info("🔔 Spam mode ON")

        @bot.on_message(filters.command("spam_off") & filters.user(self.admin_ids))
        async def spam_off(client, message):
            self.auto_spam = False
            await message.reply("🛑 Auto-spam mode turned OFF")
            logger.info("🚫 Spam mode OFF")

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
                    for chat_id in TARGET_CHAT_IDS:
                        key = (bot.name, chat_id)
                        last_time = self.last_spam_time.get(key, datetime.min)

                        if (datetime.now() - last_time) > timedelta(seconds=self.spam_interval):
                            for msg in SPAM_MESSAGES:
                                try:
                                    await bot.send_message(chat_id, msg)
                                    await asyncio.sleep(5)
                                except RPCError as e:
                                    logger.warning(f"{bot.name} to {chat_id}: {e}")
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
        print("🛑 Stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
