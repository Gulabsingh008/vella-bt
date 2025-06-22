import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors import ChatWriteForbiddenError

# Multiple Bot Configuration
BOTS_CONFIG = [
    {
        "name": "bot1",
        "api_id": 26494161,
        "api_hash": "55da841f877d16a3a806169f3c5153d3",
        "bot_token": "7670198611:AAEwf0-xqEiBHocibNAXMRqz08TIVFWz8PM",
        "log_channel": -1002246848988
    },
    {
        "name": "bot2",
        "api_id": 24519654,
        "api_hash": "1ccea9c29a420df6a6622383fbd83bcd",
        "bot_token": "7982548340:AAHEfCDzWEKMb6h6EBdwNaG1VzSvIhrMk7I",
        "log_channel": -1002246848988
    }
]

clients = []

async def start_bot(config):
    client = TelegramClient(
        session=config['name'],
        api_id=config['api_id'],
        api_hash=config['api_hash']
    ).start(bot_token=config['bot_token'])

    # Start message handler
    @client.on(events.NewMessage(pattern="/start"))
    async def handle_start(event):
        sender = await event.get_sender()
        user_mention = f"[{sender.first_name}](tg://user?id={sender.id})"
        await event.reply(f"👋 Hello! I am @{(await client.get_me()).username}")

        log_msg = (
            f"👤 User: {user_mention}\n"
            f"🆔 ID: `{sender.id}`\n"
            f"📥 Started the bot."
        )

        try:
            await client.send_message(config['log_channel'], log_msg, parse_mode="md")
        except ChatWriteForbiddenError:
            print(f"⚠️ Bot has no permission to write to log channel: {config['log_channel']}")
        except Exception as e:
            print(f"❌ Log failed: {e}")

    # Start the client
    await client.start()
    me = await client.get_me()
    print(f"✅ {config['name']} started as @{me.username}")
    clients.append(client)

    # Send "Bot Started" message to log channel
    try:
        await client.send_message(config['log_channel'], f"✅ Bot @{me.username} Started. Stay tuned!")
        print(f"📩 Log channel message sent for {config['name']}")
    except Exception as e:
        print(f"⚠️ Failed to send startup log for {config['name']}: {e}")


async def main():
    await asyncio.gather(*(start_bot(cfg) for cfg in BOTS_CONFIG))
    print("⚙️ All bots started. Waiting for events...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped.")
