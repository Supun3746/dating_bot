from aiogram import Bot

from config import settings

bot = Bot(token=settings.TOKEN.get_secret_value())
