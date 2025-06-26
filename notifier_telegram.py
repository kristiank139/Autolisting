from telegram import Bot
import os
import asyncio
from dotenv import load_dotenv

load_dotenv(".env")

async def send_telegram_message(bot_token, chat_id, message_text):
    telegram_bot = Bot(token=bot_token)
    await telegram_bot.send_message(chat_id=chat_id, text=message_text, parse_mode="HTML")

def main(message_text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    asyncio.run(send_telegram_message(bot_token, chat_id, message_text))

if __name__ == "__main__":
    main("Test")