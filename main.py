import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError, FloodWait, PeerIdInvalid
from pyrogram.types import ChatPermissions
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration from environment variables
def get_config():
    return {
        "bots": [
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
        ],
        "chat_ids": [int(id) if id.lstrip('-').isdigit() else id.strip() 
                    for id in os.getenv("CHAT_IDS", "-1002246848988").split(",")],
        "admin_ids": [int(id) for id in os.getenv("ADMIN_IDS", "1114789110").split(",") if id],
        "spam_interval": int(os.getenv("SPAM_INTERVAL", "3600")),
        "auto_spam": os.getenv("AUTO_SPAM", "True").lower() == "true",
        "chat_invite_link": os.getenv("CHAT_INVITE_LINK", "")
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
        """Initialize all bots with proper error handling"""
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

                # Join chat via invite link if provided
                if self.config["chat_invite_link"]:
                    try:
                        await bot.join_chat(self.config["chat_invite_link"])
                        logger.info(f"Joined chat using invite link")
                    except Exception as e:
                        logger.warning(f"Failed to join via invite link: {e}")

            except Exception as e:
                logger.error(f"❌ Failed to start {bot_config['name']}: {e}")
                raise

        await self._verify_chat_access()

    async def _verify_chat_access(self):
        """Verify and resolve all chat IDs with proper permissions"""
        self.resolved_chat_ids = []
        if not self.active_bots:
            return

        bot = self.active_bots[0]  # Use first bot for verification
        
        for raw_id in self.config["chat_ids"]:
            try:
                # Try to get chat details
                try:
                    chat = await bot.get_chat(raw_id)
                except PeerIdInvalid:
                    logger.error(f"Chat ID {raw_id} is invalid")
                    continue
                except Exception as e:
                    logger.warning(f"Failed to get chat {raw_id}: {e}")
                    continue

                # Check permissions differently for channels and groups
                if chat.type == "channel":
                    try:
                        member = await bot.get_chat_member(chat.id, "me")
                        if not member.can_post_messages:
                            raise Exception("Bot doesn't have post permission in channel")
                    except Exception as e:
                        logger.error(f"Permission check failed for channel {chat.id}: {e}")
                        continue

                elif chat.type in ["group", "supergroup"]:
                    try:
                        member = await bot.get_chat_member(chat.id, "me")
                        if not member.can_send_messages:
                            raise Exception("Bot doesn't have send messages permission")
                    except Exception as e:
                        logger.error(f"Permission check failed for group {chat.id}: {e}")
                        continue

                self.resolved_chat_ids.append(chat.id)
                logger.info(f"✅ Verified access to chat: {chat.title or chat.id} (Type: {chat.type})")

            except Exception as e:
                logger.error(f"❌ Final verification failed for {raw_id}: {e}")

    def _add_basic_handlers(self, bot):
        """Add basic command handlers"""
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"🤖 Hello! I'm @{client.me.username}\n"
                              f"Status: {'ACTIVE' if self.auto_spam else 'INACTIVE'}")

    def _add_control_handlers(self, bot):
        """Add admin control handlers"""
        @bot.on_message(filters.command("spam_on") & filters.user(self.admin_ids))
        async def enable_spam(client, message):
            self.auto_spam = True
            await message.reply("✅ Spam mode activated")
            logger.info("Spam mode enabled by admin")

        @bot.on_message(filters.command("spam_off") & filters.user(self.admin_ids))
        async def disable_spam(client, message):
            self.auto_spam = False
            await message.reply("🛑 Spam mode deactivated")
            logger.info("Spam mode disabled by admin")

        @bot.on_message(filters.command("status") & filters.user(self.admin_ids))
        async def show_status(client, message):
            status = [
                f"• Bots Active: {len(self.active_bots)}",
                f"• Chats Configured: {len(self.resolved_chat_ids)}",
                f"• Spam Mode: {'ON' if self.auto_spam else 'OFF'}"
            ]
            await message.reply("\n".join(status))

    async def run_spam_cycle(self):
        """Main spam cycle with improved error handling"""
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
                        try:
                            # Verify chat access first
                            try:
                                chat = await bot.get_chat(chat_id)
                            except Exception as e:
                                logger.warning(f"Re-checking chat access failed: {e}")
                                continue

                            # Send messages with delay
                            for msg in spam_messages:
                                try:
                                    await bot.send_message(chat_id, msg)
                                    await asyncio.sleep(5)  # Anti-flood delay
                                except FloodWait as e:
                                    logger.warning(f"⏳ Flood wait {e.value}s")
                                    await asyncio.sleep(e.value)
                                except RPCError as e:
                                    logger.error(f"⚠️ Error sending message: {e}")
                                    break

                            # Update last spam time
                            self.last_spam_time[(bot.name, chat_id)] = datetime.now()

                        except Exception as e:
                            logger.error(f"❌ Error in spam cycle: {e}")

            await asyncio.sleep(60)  # Check every minute

async def main():
    config = get_config()
    manager = BotManager(config)
    
    try:
        await manager.initialize_bots()
        asyncio.create_task(manager.run_spam_cycle())
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
