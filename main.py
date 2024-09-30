import asyncio
import logging

from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from bot import bot
from add_profile import router as router_create
from database import create_table
from get_profile import router as router_get

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_routers(router_create, router_get)


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer(
        "Если хотите создать профиль введите /add \nЕсли хотите посмотреть профили по фото введите /get"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(create_table())
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
