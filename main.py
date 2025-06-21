import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables (for Koyeb)
import os
BOT_TOKENS = os.getenv("BOT_TOKENS", "").split(";")  # Format: "token1;token2;control_token"
if not all(BOT_TOKENS) or len(BOT_TOKENS) < 2:
    logger.error("Invalid BOT_TOKENS configuration!")
    exit(1)
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "1114789110").split(",") if id]
SPAM_INTERVAL = int(os.getenv("SPAM_INTERVAL", 3600))  # 1 hour default

class BotManager:
    def __init__(self):
        self.auto_spam = False
        self.last_spam_time = {}
        self.bots = []
        
        if not BOT_TOKENS:
            raise ValueError("No bot tokens provided in environment variables")

        async def initialize_bots(self):
        """Initialize all bot instances with better error handling"""
        if not BOT_TOKENS:
            logger.error("No BOT_TOKENS found in environment variables!")
            return
    
        try:
            control_token = BOT_TOKENS[-1]
            worker_tokens = BOT_TOKENS[:-1]
            
            for i, token in enumerate(worker_tokens):
                if not token or ":" not in token:
                    logger.error(f"Invalid token format for bot {i}")
                    continue
                    
                try:
                    bot = Client(f"worker_{i}", bot_token=token)
                    self._add_basic_handlers(bot)
                    await bot.start()
                    self.bots.append(bot)
                    logger.info(f"Worker bot {i} started as @{bot.me.username}")
                except Exception as e:
                    logger.error(f"Failed to start worker bot {i}: {str(e)}")

        # Initialize control bot
        try:
            control_bot = Client("control_bot", bot_token=control_token)
            self._add_control_handlers(control_bot)
            await control_bot.start()
            self.bots.append(control_bot)
            logger.info(f"Control bot {control_bot.me.username} started")
        except Exception as e:
            logger.error(f"Failed to start control bot: {e}")

    def _add_basic_handlers(self, bot):
        """Add basic command handlers to worker bots"""
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"🤖 Hello! I'm {client.me.username}\n\n"
                              f"Bot status: {'ACTIVE' if self.auto_spam else 'INACTIVE'}")

    def _add_control_handlers(self, bot):
        """Add admin control handlers"""
        @bot.on_message(filters.command("spam_on") & filters.user(ADMIN_IDS))
        async def turn_on(client, message):
            self.auto_spam = True
            await message.reply("✅ Auto-spam activated")
            logger.info("Spam mode activated by admin")

        @bot.on_message(filters.command("spam_off") & filters.user(ADMIN_IDS))
        async def turn_off(client, message):
            self.auto_spam = False
            await message.reply("🛑 Auto-spam deactivated")
            logger.info("Spam mode deactivated by admin")

        @bot.on_message(filters.command("bot_status") & filters.user(ADMIN_IDS))
        async def bot_status(client, message):
            status = []
            for bot in self.bots:
                try:
                    status.append(f"• {bot.me.username}: {'🟢' if await bot.get_me() else '🔴'}")
                except:
                    status.append(f"• {bot.name}: 🔴 (Offline)")
            
            await message.reply(
                f"🤖 Bot Status:\n" + "\n".join(status) +
                f"\n\nSpam Mode: {'ON' if self.auto_spam else 'OFF'}"
            )

    async def _can_spam(self, chat_id):
        """Check if we can spam this chat (cooldown)"""
        last_time = self.last_spam_time.get(chat_id, datetime.min)
        return (datetime.now() - last_time) > timedelta(seconds=SPAM_INTERVAL)

    async def spam_channels(self):
        """Controlled spamming function"""
        while True:
            if self.auto_spam:
                for bot in self.bots[:-1]:  # Skip control bot
                    try:
                        async for dialog in bot.get_dialogs():
                            if dialog.chat.type in ["channel", "supergroup"]:
                                chat_id = dialog.chat.id
                                if await self._can_spam(chat_id):
                                    try:
                                        await bot.send_message(
                                            chat_id,
                                            "📢 Join our channel for updates!\n"
                                            "👉 @example_channel"
                                        )
                                        self.last_spam_time[chat_id] = datetime.now()
                                        logger.info(f"Sent message to {chat_id} via {bot.me.username}")
                                    except RPCError as e:
                                        logger.warning(f"Failed to send to {chat_id}: {e}")
                    except Exception as e:
                        logger.error(f"Error in spam loop: {e}")
            
            await asyncio.sleep(60)  # Check every minute

async def main():
    manager = BotManager()
    await manager.initialize_bots()
    
    # Start spam loop as background task
    asyncio.create_task(manager.spam_channels())
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
