import os
from io import BytesIO

import cv2
import numpy as np
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message, CallbackQuery

from utils import find_most_similar_user, extract_average_embedding, cosine_similarity
from bot import bot
from kb import kb_next
from forms import GetProfile

router = Router()

embedding = 0


@router.message(Command("get"))
async def start_find(msg: Message, state: FSMContext):
    await msg.answer("Отправьте фото")
    await state.set_state(GetProfile.photo)


@router.message(GetProfile.photo, F.photo)
async def first_get_similar_profile(msg: Message, state: FSMContext):
    photo = msg.photo[-1]
    user_id = msg.from_user.id

    file_info = await bot.get_file(photo.file_id)
    file_data = await bot.download_file(file_info.file_path)
    file_bytes = file_data.read()
    embedding = await extract_average_embedding(file_bytes, to_db=False)
    user = await find_most_similar_user(embedding, user_id=user_id)

    photo_file = FSInputFile(user.photo)
    await msg.answer_photo(photo_file)
    if user.user_nick:
        await msg.answer(user.user_nick)
    await msg.answer(
        f"Имя: {user.name}\nВозраст: {user.age}\nО себе: {user.description}"
    )
    await msg.answer(
        "Нажмите на кнопку чтобы посмотреть следующий профиль", reply_markup=kb_next
    )
    await state.clear()


@router.callback_query(F.data)
async def next_profile(callback: CallbackQuery):
    user = await cosine_similarity(embedding, n=2)
    photo_file = FSInputFile(user.photo)
    await callback.answer_photo(photo_file)
    if user.user_nick:
        await callback.answer(user.user_nick)
    await callback.answer(
        f"Имя: {user.name}\nВозраст: {user.age}\nО себе: {user.description}"
    )
    await callback.answer(
        "Нажмите на кнопку чтобы посмотреть следующий профиль", reply_markup=kb_next
    )
