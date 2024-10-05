import os
from datetime import datetime

from aiogram import types, F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv

from exceptions import RoundToFiveError
from filters.check_admin import IsAdmin
from keyboards.topic_choose_kbds import choose_topic_kbd, make_catalogue, topic_kbd, change_kbd, menu_kbd, \
    last_check_kbd, settings_kbd
from keyboards.user_kbds import start_kbd, make_event_catalogue, event_book_kbd, event_unbook_kbd, back_kbd
from keyboards.adm_kbds import admin_main_menu_kbd
from models import create_topic_list, change_user_subscription, get_topic_by_title, check_booking, \
    check_registration, register_user, register_answers, change_subscription_time, cancel_subscription, \
    get_event, add_booking, delete_booking, get_user_time_topic
from state.user_states import TopicChoose, Registration, BookingEvent

load_dotenv()

user_direct_router = Router()
admins = os.getenv('ADMINS').split(',')

API_TOKEN = os.getenv('TOKEN')
bot: Bot = Bot(token=API_TOKEN)


@user_direct_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if check_registration(message.chat.id):
        await message.answer(
            "Добро пожаловать",
            reply_markup=start_kbd
        )
    else:
        await bot.send_message(
            chat_id=592386558,
            text=f"@{message.from_user.username}, id: {message.from_user.id}")
        print(message.from_user.username, message.from_user.id)
        await message.answer(
            "Вас приветствует наш самый скромный бот\n"
            "Для начала напишите как вас зовут",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Registration.name)


@user_direct_router.message(Command("help"))
@user_direct_router.message(F.text.lower() == "прочитать описание")
async def cmd_help(message: types.Message):
    await message.answer(
        "НАПИСАТЬ СООБЩЕНИЕ, В КОТОРОМ БУДЕМ РАССКАЗЫВАТЬ КАК И ЧТО УМЕЕТ БОТ!\n\n"
        "Приветствуем вас тут вы можете подписаться на тему, получать каждый день картнки, описания и писать по "
        "ним вдохновленные в вас тексты. Изменить время, в которое вам будет приходить сообщение можно "
        "в настройках\n"
        "Так же вы можете записаться на мероприятие...",
        reply_markup=menu_kbd
    )


@user_direct_router.message(StateFilter(Registration.name), F.text)
async def register_q1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        f"Запишем вас как {message.text}\n\n"
        f"А теперь скажите, как часто вы пишете что-нибудь для себя"
    )

    await state.set_state(Registration.question_1)


@user_direct_router.message(StateFilter(Registration.question_1), F.text)
async def register_q2(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)

    await message.answer(
        f"Ваше любимое произведение?"
    )

    await state.set_state(Registration.question_2)


@user_direct_router.message(StateFilter(Registration.question_2), F.text)
async def register_name(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    data = await state.get_data()
    register_user(message.from_user.id)
    register_answers(message.from_user.id, message.from_user.username, data['name'], data['q1'], data['q2'])
    await message.answer(
        "Благодарим за регистрацию\n\n"
        "Подробнее о функционале бота можете прочитать нажав на кнопку \"Прочитать описание\" либо по коменде /help",
        reply_markup=start_kbd
    )
    await state.clear()


'''------------------------------------------ВЫБОР ТЕМЫ------------------------------------------------------'''


@user_direct_router.message(StateFilter(None), F.text.lower() == "выбор темы")
@user_direct_router.message(StateFilter(TopicChoose.catalogue), F.text.lower() == "назад")
@user_direct_router.message(StateFilter(TopicChoose.settings), F.text.lower() == "назад")
async def choose_topic(message: types.Message, state: FSMContext):
    time, topic, progress = get_user_time_topic(message.from_user.id)
    if time is not None:
        await state.update_data(time=time)
    if topic != 0:
        await state.update_data(cur_topic=topic, progress=progress)
        await message.answer(f"Вы подписаны на тему {topic}\n"
                             f"Ваш прогресс: {progress[0]}/{progress[1]} карточек")
    await message.answer(
        "Выбор темы:",
        reply_markup=choose_topic_kbd
    )
    await state.set_state(TopicChoose.menu)


#В клавиатуру добавил кнопку отлично потому что по какой-то причине клавиатура с одной кнопкой не отображается на айпаде
# переход в каталог тем из меню и по кнопке назад из выбранной темы
@user_direct_router.message(StateFilter(TopicChoose.menu), F.text.lower() == "каталог тем")
@user_direct_router.message(StateFilter(TopicChoose.topic), (F.text.lower() == "назад") | (F.text.lower() == "отлично"))
@user_direct_router.message(StateFilter(TopicChoose.change_topic), F.text.lower() == "оставить старую тему")
async def choose_topic(message: types.Message, state: FSMContext):
    await message.answer(
        "Каталог тем:",
        reply_markup=make_catalogue()
    )
    await state.set_state(TopicChoose.catalogue)


# todo: можно обойти этот пункт, если написать 'подписаться' руками. Не критично, но можно исправить
# переход в описание темы с кнопками подписаться и назад
@user_direct_router.message(StateFilter(TopicChoose.catalogue), F.text.in_(create_topic_list()))
async def topic1(message: types.Message, state: FSMContext):
    topic = get_topic_by_title(message.text)
    data = await state.get_data()
    kbd = change_kbd if 'cur_topic' in data else topic_kbd
    if 'cur_topic' in data and data['cur_topic'] == message.text:
        await message.answer("Вы уже подписаны на эту тему")
        kbd = back_kbd

    await state.update_data(topic_title=message.text)
    await message.answer(
        "<b>"+topic.title+"</b>" + "\n" + topic.description,
        reply_markup=kbd
    )
    await state.update_data(chosen_topic_id=topic.id)
    await state.set_state(TopicChoose.topic)


# Подписаться / Точно подписаться
@user_direct_router.message(StateFilter(TopicChoose.change_topic), F.text.lower() == "изменить тему на новую")
@user_direct_router.message(StateFilter(TopicChoose.topic), F.text.lower() == "подписаться")
async def subscribe(message: types.Message, state: FSMContext):
    data = await state.get_data()
    change_user_subscription(message.chat.id, data['chosen_topic_id'])
    if 'time' not in data:
        await message.answer(
            f"Вы подписались на тему <b>{data['topic_title']}</b>\n\n"
            "В течение нескольких минут вам придет карточка.\n"
            "В дальнейшем будет приходить в это же время. Изменить время получения карточки можно в настройках"
        )
    else:
        await message.answer(
            f"Вы подписались на тему <b>{data['topic_title']}</b>\n\n"
            f"Карточка вам придет в {data['time']} МСК\n"
            "Изменить время получения карточки можно в настройках"
        )
    await cancel(message, state)


# Спросить точно ли хотят изменить подписку
@user_direct_router.message(StateFilter(TopicChoose.topic), F.text.lower() == "изменить тему")
async def ask_if_really_wants(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"Вы уже подписаны на тему {data['cur_topic']}\n"
        f"Ваш прогресс = {data['progress'][0]} / {data['progress'][1]}\n"
        "Действительно ли вы хотите изменить тему подписки?",
        reply_markup=last_check_kbd)
    await state.set_state(TopicChoose.change_topic)


@user_direct_router.message(StateFilter(TopicChoose.menu), F.text.lower() == "настройки")
async def settings_menu(message: types.Message, state: FSMContext):
    await message.answer(
        "Настройки",
        reply_markup=settings_kbd)
    await state.set_state(TopicChoose.settings)


@user_direct_router.message(StateFilter(TopicChoose.settings), F.text.lower() == "изменить время получения картинки")
async def ask_time(message: types.Message, state: FSMContext):
    await message.answer(
        "Напишите время (МСК), в которое вы бы хотели получать рассылку карточек,"
        "округленное до 5 минут в формате чч:мм\n\n"
        "Для выхода напишите \"Назад\"",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(TopicChoose.ask_time)


@user_direct_router.message(StateFilter(TopicChoose.ask_time), F.text.lower() == 'назад')
async def change_time(message: types.Message, state: FSMContext):
    await cancel(message, state)


@user_direct_router.message(StateFilter(TopicChoose.ask_time), F.text)
async def change_time(message: types.Message, state: FSMContext):
    try:
        new_time = datetime.strptime(message.text, '%H:%M')
        if new_time.minute % 5 != 0:
            raise RoundToFiveError
    except ValueError:
        await message.answer("Неверный формат! \nНапишите время округленное до 5 минут в формате ЧЧ:ММ")
    except RoundToFiveError:
        await message.answer("Неверный формат! \nОкруглите минуты до 5!")
    else:
        change_subscription_time(message.from_user.id, new_time)
        await message.answer(
            "Время изменено \n"
            "Настройки:",
            reply_markup=settings_kbd)
        await state.set_state(TopicChoose.settings)


@user_direct_router.message(StateFilter(TopicChoose.settings), F.text.lower() == "приостановить подписку")
async def pause_subscription(message: types.Message, state: FSMContext):
    if cancel_subscription(message.from_user.id):
        await message.answer(
            "Ваша текущая подписка приостановлена\n"
            "Для возобновления подпишитесь на тему через каталог тем")
    else:
        await message.answer("У вас нет активных подписок")
    await cancel(message, state)


'''----------------------------------------ЗАПИСЬ НА МЕРОПРИЯТИЕ----------------------------------------------------'''


@user_direct_router.message(StateFilter(None), F.text.lower() == "мероприятия")
@user_direct_router.message(StateFilter(BookingEvent.event), F.text.lower() == "назад")
async def events_list(message: types.Message, state: FSMContext):
    events_number, events_kbd = make_event_catalogue()
    if events_number == 0:
        await message.answer("В ближайшее время мероприятий не запланировано")
    else:
        await message.answer(
            "Вот грядущие мероприятия:",
            reply_markup=events_kbd
        )
        await state.set_state(BookingEvent.catalogue)


@user_direct_router.message(StateFilter(BookingEvent.catalogue), F.text)
async def event_about(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await cancel(message, state)
    else:
        event_title, event_date = message.text.split('\n')
        event = get_event(event_title, event_date)
        if event:
            await state.update_data(event_id=event.id, event_title=event.title)
            if check_booking(message.from_user.id, event.id):
                await message.answer(f"Вы записаны на событие {event.title}", reply_markup=event_unbook_kbd)
            else:
                await message.answer(f"Вот такое планируется событие:\n\n"
                                     f"{event_title}\n{event.description}", reply_markup=event_book_kbd)
            await state.set_state(BookingEvent.event)


@user_direct_router.message(StateFilter(BookingEvent.event), F.text.lower() == 'записаться на мероприятие')
async def book_event(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_booking(data['event_id'], message.from_user.id)
    await bot.send_message(chat_id=273537230,
                           text=f"Пользователь @{message.from_user.username} "
                                f"записался на мероприятие {data['event_title']}")
    await message.answer("Вы записались на мероприятие")
    await events_list(message, state)


@user_direct_router.message(StateFilter(BookingEvent.event), F.text.lower() == 'отписаться от мероприятия')
async def cancel_booking(message: types.Message, state: FSMContext):
    data = await state.get_data()
    delete_booking(data['event_id'], message.from_user.id)
    await bot.send_message(chat_id=273537230,
                           text=f"Пользователь @{message.from_user.username} "
                                f"отписался от мероприятия {data['event_title']}")
    await message.answer("Вы отписались от мероприятия")
    await cancel(message, state)


'''------------------------------------------ГЛАВНОЕ МЕНЮ------------------------------------------------------'''


@user_direct_router.message(Command("main_menu"), IsAdmin())
@user_direct_router.message(F.text.lower() == "главное меню", IsAdmin())
@user_direct_router.message(StateFilter(None), F.text, IsAdmin())
async def admin_cancel(message: types.Message, state: FSMContext):
    await message.answer(
        "Главное меню:",
        reply_markup=admin_main_menu_kbd
    )
    await state.clear()


#подумать над фильтром, который будет проверять регистрацию
@user_direct_router.message(Command("main_menu"))
@user_direct_router.message(F.text.lower() == "главное меню")
@user_direct_router.message(StateFilter(None), F.text)  # Чтобы при нажатии на любую кнопку при перезагрузке бота открывалось меню
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(
        "Главное меню:",
        reply_markup=menu_kbd
    )
    await state.clear()

# старая функция получения картинки для памяти
# @user_direct_router.message(F.text.lower() == 'хочу картинку')
# async def send_photo(message: types.message):
#     pic_id, tg_id, folder, text = get_pic()
#     if not tg_id:
#         img = FSInputFile(folder)
#         msg = await message.answer_photo(
#             photo=img,
#             caption=text)
#         photo_id = msg.photo[-1].file_id
#         add_tg_id(pic_id, photo_id)
#
#     else:
#         await message.answer_photo(
#             photo=tg_id,
#             caption=text)
