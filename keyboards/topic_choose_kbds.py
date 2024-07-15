from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from models import create_topic_list

menu_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мероприятия")],
            [KeyboardButton(text="Выбор темы")]
        ],
        resize_keyboard=True
    )

choose_topic_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог тем")],
        [KeyboardButton(text="Настройки")],
        [KeyboardButton(text="Главное меню")]
    ],
    resize_keyboard=True
)

ctlg = [[KeyboardButton(text=topic)] for topic in create_topic_list()]
ctlg.append([KeyboardButton(text="Назад")])
catalogue_kbd = ReplyKeyboardMarkup(
    keyboard=ctlg,
    resize_keyboard=True
)

topic_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подписаться")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

change_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить тему")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)
