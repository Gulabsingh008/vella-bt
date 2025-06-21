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
# main.py की शुरुआत में ये डीबग लाइनें जोड़ें
print("Actual BOT1_TOKEN:", repr(os.getenv("BOT1_TOKEN")))
print("Actual BOT2_TOKEN:", repr(os.getenv("BOT2_TOKEN")))
print("Actual CONTROL_BOT_TOKEN:", repr(os.getenv("CONTROL_BOT_TOKEN")))

# main.py में शुरुआत में जोड़ें
print("BOT1_TOKEN first 5 chars:", repr(os.getenv("BOT1_TOKEN")[:5]),
print("BOT1_TOKEN last 5 chars:", repr(os.getenv("BOT1_TOKEN")[-5:]),
# main.py में शुरुआत में जोड़ें
print("BOT2_TOKEN first 5 chars:", repr(os.getenv("BOT2_TOKEN")[:5]),
print("BOT2_TOKEN last 5 chars:", repr(os.getenv("BOT2_TOKEN")[-5:])



class BotManager:
    def __init__(self):
        # सभी बॉट्स के टोकन्स (अलग-अलग वेरिएबल्स से)
        self.bot_tokens = {
            "worker1": "BOT1_TOKEN",
            "worker2": "BOT2_TOKEN",
            "control": "CONTROL_BOT_TOKEN"
        }
        
        self.admin_ids = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
        self.spam_interval = int(os.getenv("SPAM_INTERVAL", 3600))  # डिफॉल्ट 1 घंटा
        self.auto_spam = False
        self.last_spam_time = {}
        self.active_bots = []

    def validate_tokens(self):
    """सभी टोकन्स को सख्ती से वैलिडेट करें"""
        for name, token in self.bot_tokens.items():
            # टोकन को साफ करें
            cleaned_token = token.strip()
            
            # टोकन फॉर्मेट चेक करें (19:35... जैसा पैटर्न)
            if (not cleaned_token or 
                len(cleaned_token.split(':')) != 2 or 
                not cleaned_token.split(':')[0].isdigit() or 
                not cleaned_token.split(':')[1].startswith('AA')):
                
                logger.error(f"अमान्य टोकन {name}: {repr(token)}")
                logger.error(f"साफ किया गया टोकन: {repr(cleaned_token)}")
                return False
                
            self.bot_tokens[name] = cleaned_token
        return True

    async def initialize_bots(self):
        """सभी बॉट्स को इनिशियलाइज़ करें"""
        if not self.validate_tokens():
            raise ValueError("एक या अधिक बॉट टोकन अमान्य हैं")

        # वर्कर बॉट्स स्टार्ट करें
        for name, token in self.bot_tokens.items():
            if name == "control":
                continue
                
            try:
                bot = Client(name, bot_token=token)
                self._add_basic_handlers(bot)
                await bot.start()
                self.active_bots.append(bot)
                logger.info(f"✅ {name} बॉट स्टार्ट हो गया @{bot.me.username}")
            except Exception as e:
                logger.error(f"❌ {name} बॉट स्टार्ट नहीं हो पाया: {str(e)}")

        # कंट्रोल बॉट स्टार्ट करें
        try:
            control_bot = Client("control", bot_token=self.bot_tokens["control"])
            self._add_control_handlers(control_bot)
            await control_bot.start()
            self.active_bots.append(control_bot)
            logger.info(f"🎛 कंट्रोल बॉट स्टार्ट हो गया @{control_bot.me.username}")
        except Exception as e:
            logger.error(f"❌ कंट्रोल बॉट स्टार्ट नहीं हो पाया: {str(e)}")

    def _add_basic_handlers(self, bot):
        """बेसिक कमांड हैंडलर्स जोड़ें"""
        @bot.on_message(filters.command("start"))
        async def start_handler(client, message):
            await message.reply(f"🤖 नमस्ते! मैं {client.me.username} बॉट हूँ\n"
                              f"स्टेटस: {'सक्रिय' if self.auto_spam else 'निष्क्रिय'}")

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

        @bot.on_message(filters.command("status") & filters.user(self.admin_ids))
        async def bot_status(client, message):
            status = []
            for bot in self.active_bots:
                try:
                    status.append(f"• @{bot.me.username}: {'🟢' if await bot.get_me() else '🔴'}")
                except:
                    status.append(f"• {bot.name}: 🔴 (ऑफ़लाइन)")
            
            await message.reply(
                "🤖 बॉट स्टेटस:\n" + "\n".join(status) +
                f"\n\nस्पैम मोड: {'चालू' if self.auto_spam else 'बंद'}"
            )

    async def spam_channels(self):
        """चैनल्स को मैसेज भेजने का मुख्य लूप"""
        while True:
            if self.auto_spam:
                for bot in self.active_bots[:-1]:  # कंट्रोल बॉट को छोड़कर
                    try:
                        async for dialog in bot.get_dialogs():
                            if dialog.chat.type in ["channel", "supergroup"]:
                                chat_id = dialog.chat.id
                                last_time = self.last_spam_time.get(chat_id, datetime.min)
                                
                                if (datetime.now() - last_time) > timedelta(seconds=self.spam_interval):
                                    try:
                                        await bot.send_message(
                                            chat_id,
                                            "📢 हमारे चैनल से जुड़ें!\n"
                                            "👉 @example_channel"
                                        )
                                        self.last_spam_time[chat_id] = datetime.now()
                                        logger.info(f"{bot.me.username} ने {chat_id} को मैसेज भेजा")
                                    except RPCError as e:
                                        logger.warning(f"मैसेज भेजने में असफल: {e}")
                    except Exception as e:
                        logger.error(f"स्पैम लूप में त्रुटि: {e}")
            
            await asyncio.sleep(60)  # हर मिनट चेक करें

async def main():
    manager = BotManager()
    await manager.initialize_bots()
    
    # स्पैम टास्क बैकग्राउंड में शुरू करें
    asyncio.create_task(manager.spam_channels())
    
    # बॉट को रनिंग रखें
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        # शुरुआत में लोड किए गए वेरिएबल्स चेक करें (डीबगिंग के लिए)
        logger.info("बॉट शुरू हो रहा है...")
        logger.info(f"BOT1_TOKEN: {'मौजूद' if os.getenv('BOT1_TOKEN') else 'नहीं मिला'}")
        logger.info(f"BOT2_TOKEN: {'मौजूद' if os.getenv('BOT2_TOKEN') else 'नहीं मिला'}")
        logger.info(f"CONTROL_BOT_TOKEN: {'मौजूद' if os.getenv('CONTROL_BOT_TOKEN') else 'नहीं मिला'}")
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("बॉट बंद किया जा रहा है...")
    except Exception as e:
        logger.error(f"गंभीर त्रुटि: {str(e)}")
