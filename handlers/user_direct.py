from aiogram import types, F, Router
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from db import get_pic, add_tg_id, get_users_for_daily_send, check_registration, check_cur_subscription
from keyboards.topic_choose_kbds import choose_topic_kbd, catalogue_kbd, topic_kbd, change_kbd, menu_kbd
from models import create_topic_list, change_user_subscription
from state.user_states import TopicChoose

user_direct_router = Router()


@user_direct_router.message(Command("start"))
async def cmd_start(message: types.Message):
    if check_registration(message.chat.id):
        print('Пользователь есть в таблице')

    builder1 = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начинаем пользоваться")],
            [KeyboardButton(text="Прочитать описание")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Начальные кнопки. Тут потом будет опрос, если его не проходили, и главное меню, если прошли",
        reply_markup=builder1
    )


# @user_direct_router.message(Command("main_menu"), F.from_user.id == 592386558)
# async def cmd_special_buttons(message: types.Message):
#     builder = ReplyKeyboardBuilder()
#     builder.row(
#         types.KeyboardButton(text="Хочу картинку", ),
#         types.KeyboardButton(text="Купить материалы")
#     )
#
#     builder.row(
#         types.KeyboardButton(text="Посмотреть мероприятия"),
#         types.KeyboardButton(text="Админская кнопка")
#     )
#
#     await message.answer(
#         "Выберите действие:",
#         reply_markup=builder.as_markup(resize_keyboard=True)
#     )


@user_direct_router.message(Command("main_menu"))
@user_direct_router.message(F.text.lower() == "главное меню")
@user_direct_router.message(F.text == "Начинаем пользоваться")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(
        "Главное меню:",
        reply_markup=menu_kbd
    )

    await state.clear()
    print(await state.get_state())


@user_direct_router.message(StateFilter(None), F.text.lower() == "выбор темы")
@user_direct_router.message(StateFilter(TopicChoose.catalogue), F.text.lower() == "назад")
async def choose_topic(message: types.Message, state: FSMContext):
    await message.answer(
        "Выбор темы:",
        reply_markup=choose_topic_kbd
    )
    await state.set_state(TopicChoose.menu)


# переход в каталог тем из меню и по кнопке назад из выбранной темы
@user_direct_router.message(StateFilter(TopicChoose.menu), F.text.lower() == "каталог тем")
@user_direct_router.message(StateFilter(TopicChoose.topic), F.text.lower() == "назад")
async def choose_topic(message: types.Message, state: FSMContext):
    await message.answer(
        "Каталог тем:",
        reply_markup=catalogue_kbd
    )
    await state.set_state(TopicChoose.catalogue)


# переход в описание темы с кнопками подписаться и назад
@user_direct_router.message(StateFilter(TopicChoose.catalogue), F.text.in_(create_topic_list()))
async def topic1(message: types.Message, state: FSMContext):
    # kbd = change_kbd if check_cur_subscription(message.chat.id) else topic_kbd
    kbd = topic_kbd
    await message.answer(
        "Тема 1 представляет из себя ... \n"
        "в ней 30 карточек",
        reply_markup=kbd
    )
    await state.set_state(TopicChoose.topic)


# Подписаться
@user_direct_router.message(StateFilter(TopicChoose.topic), F.text.lower() == "подписаться")
async def subscribe(message: types.Message, state: FSMContext):

    change_user_subscription(message.chat.id, 2)
    await message.answer(
        "Вы подписались на тему\n"
        "Вы молодец!\n"
        "я тоже",
        reply_markup=menu_kbd)
    await state.clear()


@user_direct_router.message(F.text.lower() == 'хочу картинку')
async def send_photo(message: types.message):
    pic_id, tg_id, folder, text = get_pic()
    print(message)
    if not tg_id:
        img = FSInputFile(folder)
        msg = await message.answer_photo(
            photo=img,
            caption=text)
        photo_id = msg.photo[-1].file_id
        add_tg_id(pic_id, photo_id)

    else:
        await message.answer_photo(
            photo=tg_id,
            caption=text)


@user_direct_router.message(F.text.lower() == 'список')
async def print_list(message: types.message):
    get_users_for_daily_send()


@user_direct_router.message(F.text.lower() == 'чек')
async def check_sub(message: types.message):
    user_id = message.chat.id
    change_user_subscription(user_id, 1)

