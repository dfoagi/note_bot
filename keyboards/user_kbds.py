from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from models import create_events_list

start_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Главное меню")],
        [KeyboardButton(text="Прочитать описание")]
    ],
    resize_keyboard=True
)


def make_event_catalogue():
    ctlg = [[KeyboardButton(text=f'{event.title}\n{event.date}')] for event in create_events_list()]
    events_number = len(ctlg)
    ctlg.append([KeyboardButton(text="Назад")])
    catalogue_kbd = ReplyKeyboardMarkup(
        keyboard=ctlg,
        resize_keyboard=True
        )
    return [events_number, catalogue_kbd]


event_book_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Записаться на мероприятие")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

event_unbook_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отписаться от мероприятия")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

back_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отлично")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)
