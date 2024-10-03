from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_main_menu_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мероприятия")],
            [KeyboardButton(text="Выбор темы")],
            [KeyboardButton(text="Админская панель")]
        ],
        resize_keyboard=True
    )

admin_menu_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать анонс")],
            [KeyboardButton(text="Создать мероприятие")],
            [KeyboardButton(text="Редактировать карточку")],
            [KeyboardButton(text="Главное меню")]
        ],
        resize_keyboard=True
    )

choose_type_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Платное")],
        [KeyboardButton(text="Бесплатное")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

save_event_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сохранить")],
        [KeyboardButton(text="Назад")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

save_announcement_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить всем")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

choose_part_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить картинку")],
        [KeyboardButton(text="Изменить текст")]
    ],
    resize_keyboard=True
)

card_check = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сохранить")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)
