from aiogram.fsm.state import State, StatesGroup


class CreateProfile(StatesGroup):
    photo = State()
    name = State()
    age = State()
    gender = State()
    find_gender = State()
    description = State()
    confirm = State()


class GetProfile(StatesGroup):
    photo = State()
