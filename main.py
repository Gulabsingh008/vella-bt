import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError, FloodWait, PeerIdInvalid
from datetime import datetime, timedelta

# ✅ Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ✅ Load configuration
def get_config():
    return {
        "bots": [
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
        ],
        "chat_ids": [-1002246848988],
        "admin_ids": [1114789110],
        "spam_interval": 3600,
        "auto_spam": True
    }

class BotManager:
    def __init__(self, config):
        self.config = config
        self.auto_spam = config["auto_spam"]
        self.spam_interval = config["spam_interval"]
        self.last_spam_time = {}
        self.admin_ids = config["admin_ids"]
        self.active_bots = []
        self.resolved_chat_ids = []

    async def initialize_bots(self):
        for bot_config in self.config["bots"]:
            try:
                bot = Client(
                    name=bot_config["name"],
                    api_id=bot_config["api_id"],
                    api_hash=bot_config["api_hash"],
                    bot_token=bot_config["bot_token"],
                    in_memory=True
                )

                if bot_config["name"] == "control_bot":
                    self._add_control_handlers(bot)
                else:
                    self._add_basic_handlers(bot)

                await bot.start()
                me = await bot.get_me()
                logger.info(f"✅ Started {bot_config['name']} as @{me.username}")
                self.active_bots.append(bot)

            except Exception as e:
                logger.error(f"❌ Failed to start {bot_config['name']}: {e}")
                raise

        await self._verify_chat_access()

    async def _verify_chat_access(self):
        self.resolved_chat_ids = []
        if not self.active_bots:
            return

        bot = self.active_bots[0]
        for raw_id in self.config["chat_ids"]:
            try:
                chat = await bot.get_chat(raw_id)
                self.resolved_chat_ids.append(chat.id)
                logger.info(f"✅ Verified chat access: {chat.title or chat.id}")
            except Exception as e:
                logger.error(f"❌ Chat access failed for {raw_id}: {e}")

    def _add_basic_handlers(self, bot):
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply_text(f"🤖 Hello from @{client.me.username}!")

    def _add_control_handlers(self, bot):
        @bot.on_message(filters.command("spam_on") & filters.user(self.admin_ids))
        async def enable_spam(client, message):
            self.auto_spam = True
            await message.reply("✅ Spam mode activated.")
            logger.info("🔛 Spam ON by admin.")

        @bot.on_message(filters.command("spam_off") & filters.user(self.admin_ids))
        async def disable_spam(client, message):
            self.auto_spam = False
            await message.reply("🛑 Spam mode deactivated.")
            logger.info("🔴 Spam OFF by admin.")

        @bot.on_message(filters.command("status") & filters.user(self.admin_ids))
        async def show_status(client, message):
            bot_usernames = [f"@{(await b.get_me()).username}" for b in self.active_bots]
            msg = (
                f"🤖 Bots Running: {', '.join(bot_usernames)}\n"
                f"💬 Target Chats: {len(self.resolved_chat_ids)}\n"
                f"🔁 Spam Mode: {'ON' if self.auto_spam else 'OFF'}\n"
                f"⏱ Interval: {self.spam_interval}s"
            )
            await message.reply(msg)

    async def run_spam_cycle(self):
        spam_messages = [
            "🔥 Follow our channel!",
            "📢 Check today's update!",
            "📡 Tech, Jobs and Fun in one place!",
            "🎯 Content that makes you Grow!",
            "🧠 Get Daily Knowledge Boost!"
        ]

        while True:
            if self.auto_spam and self.resolved_chat_ids:
                for bot in self.active_bots:
                    if "control" in bot.name:
                        continue

                    for chat_id in self.resolved_chat_ids:
                        key = (bot.name, chat_id)
                        last_time = self.last_spam_time.get(key, datetime.min)
                        if (datetime.now() - last_time) > timedelta(seconds=self.spam_interval):
                            for msg in spam_messages:
                                try:
                                    await bot.send_message(chat_id, msg)
                                    await asyncio.sleep(5)
                                except FloodWait as e:
                                    await asyncio.sleep(e.value)
                                except RPCError as e:
                                    logger.warning(f"{bot.name} → {chat_id}: {e}")
                            self.last_spam_time[key] = datetime.now()
            await asyncio.sleep(60)

async def main():
    config = get_config()
    manager = BotManager(config)
    await manager.initialize_bots()
    asyncio.create_task(manager.run_spam_cycle())
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped.")
    except Exception as e:
        logger.error(f"💥 Fatal: {e}")
