import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from utils import extract_average_embedding
from bot import bot
from config import settings
from database import Men, Women, db
from forms import CreateProfile
from kb import kb_man_woman, kb_yes_no

router = Router()


@router.message(Command("add"))
async def start_create_profile(msg: Message, state: FSMContext):
    await msg.answer("Введите имя")
    await state.set_state(CreateProfile.name)


@router.message(CreateProfile.name, F.text)
async def get_name_user(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите ваш возраст")
    await state.set_state(CreateProfile.age)


@router.message(CreateProfile.age, F.text)
async def get_age_user(msg: Message, state: FSMContext):
    try:
        age = int(msg.text)
        await state.update_data(age=age)
        await msg.answer("Выберите ваш пол", reply_markup=kb_man_woman)
        await state.set_state(CreateProfile.gender)
    except:
        await msg.answer("Введите цифры")
        await state.set_state(CreateProfile.age)


@router.callback_query(F.data.in_(["man", "woman"]))
async def get_gender_user(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    gender_to_bool = lambda n: True if n == "man" else False

    if current_state == CreateProfile.gender:
        await state.update_data(gender=gender_to_bool(callback.data))
        await callback.message.answer("Я ищу", reply_markup=kb_man_woman)
        await state.set_state(CreateProfile.find_gender)

    elif current_state == CreateProfile.find_gender:
        await state.update_data(find_gender=gender_to_bool(callback.data))
        await callback.message.answer("Опишите себя")
        await state.set_state(CreateProfile.description)

    await callback.answer()


@router.message(CreateProfile.description, F.text)
async def get_desc_by_user(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await msg.answer("Загрузите фото вашего профиля")
    await state.set_state(CreateProfile.photo)


@router.message(CreateProfile.photo, F.photo)
async def get_photo_by_user(msg: Message, state: FSMContext):
    photo = msg.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = os.path.join(settings.USERS, f"{msg.from_user.id}.jpg")

    await bot.download_file(file.file_path, destination=file_path)

    await state.update_data(photo=file_path)

    user_data = await state.get_data()

    photo = FSInputFile(user_data["photo"])

    await bot.send_photo(msg.chat.id, photo)
    to_gender = lambda n: "Мужской" if n else "Женский"
    await msg.answer(
        f"Ваше имя: {user_data['name']}\nВаш возраст: {user_data['age']}\nВаш пол: {to_gender(user_data['gender'])}\nВы ищите: {to_gender(user_data['find_gender'])}\nО себе: {user_data['description']}"
    )
    await msg.answer("Все верно?", reply_markup=kb_yes_no)

    await state.set_state(CreateProfile.confirm)


@router.callback_query(F.data.in_(["yes", "no"]))
async def confirm_profile(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    if action == "yes":
        await callback.message.answer("Отлично! Данные сохранены.")

        user_data = await state.get_data()
        # user_id = callback.from_user.id
        # user_nick = callback.from_user.username
        # name = user_data.get("name")
        # age = user_data.get("age")
        # gender = user_data.get("gender")
        # find_gender = user_data.get("find_gender")
        # description = user_data.get("description")
        # photo = user_data.get("photo")
        # photo_embedding = await extract_average_embedding(photo, to_db=True)

        data = dict(
            user_id=callback.from_user.id,
            user_nick=callback.from_user.username,
            name=user_data.get("name"),
            age=user_data.get("age"),
            gender=user_data.get("gender"),
            find_gender=user_data.get("find_gender"),
            description=user_data.get("description"),
            photo=user_data.get("photo"),
            photo_embedding=await extract_average_embedding(
                user_data.get("photo"), to_db=True
            ),
        )

        async with db.session_factory() as session:

            if data["gender"]:
                # user = Men(
                #     user_id=user_id,
                #     user_nick=user_nick,
                #     name=name,
                #     age=age,
                #     find_gender=find_gender,
                #     description=description,
                #     photo=photo,
                #     photo_embedding=photo_embedding,
                # )
                pass
            else:
                user = Women(**data)
            session.add(user)
            await session.commit()

        await state.clear()
    else:
        await callback.message.answer("Давай начнем сначала. Загрузи свое фото")
        await state.set_state(CreateProfile.photo)
    await callback.answer()
