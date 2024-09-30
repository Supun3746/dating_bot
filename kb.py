from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


kb_yes_no = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes")],
        [InlineKeyboardButton(text="Нет", callback_data="no")],
    ],
)
kb_man_woman = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="man")],
        [InlineKeyboardButton(text="Женский", callback_data="woman")],
    ]
)

kb_next = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Далее", callback_data="next")]]
)
