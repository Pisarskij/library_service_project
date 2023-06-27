from aiogram import Bot
import os
from asgiref.sync import async_to_sync

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))


async def async_send_message(text: str):
    await bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=text)


def send_message(text: str):
    async_to_sync(async_send_message)(text)
