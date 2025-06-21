import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from datetime import datetime, timedelta

# लॉगिंग कॉन्फिगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        # सभी बॉट्स के क्रेडेंशियल्स
        self.bots_config = [
            {
                "name": "bot1",
                "api_id": int(os.getenv("BOT1_API_ID")),
                "api_hash": os.getenv("BOT1_API_HASH"),
                "bot_token": os.getenv("BOT1_TOKEN")
            },
            {
                "name": "bot2", 
                "api_id": int(os.getenv("BOT2_API_ID")),
                "api_hash": os.getenv("BOT2_API_HASH"),
                "bot_token": os.getenv("BOT2_TOKEN")
            },
            {
                "name": "control_bot",
                "api_id": int(os.getenv("CONTROL_API_ID")),
                "api_hash": os.getenv("CONTROL_API_HASH"),
                "bot_token": os.getenv("CONTROL_BOT_TOKEN")
            }
        ]
        
        self.admin_ids = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
        self.spam_interval = int(os.getenv("SPAM_INTERVAL", 3600))  # डिफॉल्ट 1 घंटा
        self.auto_spam = False
        self.last_spam_time = {}
        self.active_bots = []

    def validate_credentials(self):
        """सभी क्रेडेंशियल्स वैलिडेट करें"""
        for bot in self.bots_config:
            if not all(bot.values()):
                logger.error(f"अमान्य क्रेडेंशियल्स: {bot['name']}")
                return False
                
            if ":" not in bot["bot_token"]:
                logger.error(f"अमान्य टोकन फॉर्मेट: {bot['name']}")
                return False
                
        return True

    async def initialize_bots(self):
        """सभी बॉट्स को इनिशियलाइज़ करें (Pyrogram v2+ कंपेटिबल)"""
        if not self.validate_credentials():
            raise ValueError("एक या अधिक बॉट क्रेडेंशियल्स अमान्य हैं")

        for config in self.bots_config:
            try:
                bot = Client(
                    name=config["name"],
                    api_id=config["api_id"],
                    api_hash=config["api_hash"],
                    bot_token=config["bot_token"],
                    in_memory=True  # Pyrogram v2+ के लिए जरूरी
                )
                
                # कंट्रोल बॉट के लिए विशेष हैंडलर्स
                if config["name"] == "control_bot":
                    self._add_control_handlers(bot)
                else:
                    self._add_basic_handlers(bot)
                    
                await bot.start()
                self.active_bots.append(bot)
                logger.info(f"✅ {config['name']} स्टार्ट हो गया @{(await bot.get_me()).username}")
                
            except Exception as e:
                logger.error(f"❌ {config['name']} स्टार्ट नहीं हो पाया: {str(e)}")
                raise

    def _add_basic_handlers(self, bot):
        """बेसिक कमांड हैंडलर्स जोड़ें"""
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"🤖 नमस्ते! मैं {client.me.username} बॉट हूँ")

    def _add_control_handlers(self, bot):
        """एडमिन कंट्रोल हैंडलर्स जोड़ें"""
        @bot.on_message(filters.command("spam_on") & filters.user(self.admin_ids))
        async def turn_on(client, message):
            self.auto_spam = True
            await message.reply("✅ स्पैम मोड चालू हो गया")
            logger.info("स्पैम मोड चालू (एडमिन द्वारा)")

        @bot.on_message(filters.command("spam_off") & filters.user(self.admin_ids))
        async def turn_off(client, message):
            self.auto_spam = False
            await message.reply("🛑 स्पैम मोड बंद हो गया")
            logger.info("स्पैम मोड बंद (एडमिन द्वारा)")

    async def spam_channels(self):
        """चैनल्स को मैसेज भेजने का मुख्य लूप"""
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
                    if "control" in bot.name:  # कंट्रोल बॉट को छोड़ें
                        continue
                        
                    try:
                        async for dialog in bot.get_dialogs():
                            if dialog.chat.type in ["channel", "supergroup"]:
                                chat_id = dialog.chat.id
                                last_time = self.last_spam_time.get(chat_id, datetime.min)
                                
                                if (datetime.now() - last_time) > timedelta(seconds=self.spam_interval):
                                    for msg in SPAM_MESSAGES:
                                        try:
                                            await bot.send_message(chat_id, msg)
                                            await asyncio.sleep(5)  # Anti-spam delay
                                        except RPCError as e:
                                            logger.warning(f"{bot.me.username}: {e}")
                                    
                                    self.last_spam_time[chat_id] = datetime.now()
                    except Exception as e:
                        logger.error(f"त्रुटि: {bot.name} - {str(e)}")
            
            await asyncio.sleep(60)  # हर मिनट चेक करें

async def main():
    manager = BotManager()
    await manager.initialize_bots()
    asyncio.create_task(manager.spam_channels())
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("बॉट बंद किया जा रहा है...")
    except Exception as e:
        logger.error(f"गंभीर त्रुटि: {str(e)}")
