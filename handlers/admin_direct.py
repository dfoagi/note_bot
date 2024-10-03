from aiogram import types, F, Router
from aiogram.filters import StateFilter, command
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime, time

from exceptions import WrongLastNumber
from filters.check_admin import IsAdmin
from keyboards.topic_choose_kbds import make_catalogue
from keyboards.adm_kbds import admin_menu_kbd, choose_type_kbd, save_event_kbd, save_announcement_kbd, card_check, \
    admin_main_menu_kbd
from state.user_states import CreateEvent, CreateAnnouncement, ChangeCard
from models import add_event, send_announcement, create_topic_list, get_topic_by_title, send_chosen_card, change_card
from parse_pics import parse_topics

admin_direct_router = Router()


@admin_direct_router.message(StateFilter(None), F.text.lower() == "админская панель", IsAdmin())
@admin_direct_router.message(F.text.lower() == "отмена", IsAdmin())
async def admin_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Для выхода из любого пункта меню сюда напиши \"Отмена\"\n\nМеню:",
        reply_markup=admin_menu_kbd
    )


'''----------------------------------------создание анонса------------------------------------------------------'''


@admin_direct_router.message(StateFilter(None), F.text.lower() == "создать анонс", IsAdmin())
async def add_text(message: types.Message, state: FSMContext):
    await message.answer(
        "Создаем анонс для всех пользователей! \n\n"
        "Напиши текст сообщения",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(CreateAnnouncement.text)


@admin_direct_router.message(StateFilter(CreateAnnouncement.text), F.text)
async def add_picture(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Отправь картинку, которую прикрепим к сообщению \n"
                         "Отправить сообщение без картинки, напиши \"Нет\"")
    await state.set_state(CreateAnnouncement.picture)


@admin_direct_router.message(StateFilter(CreateAnnouncement.picture), F.text.lower() == 'нет')
@admin_direct_router.message(StateFilter(CreateAnnouncement.picture), F.photo)
async def check_announcement(message: types.Message, state: FSMContext):
    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(img=photo_id)

    data = await state.get_data()
    await message.answer('Письмо будет выглядеть так:')
    if 'img' not in data:
        await message.answer(f"{data['text']}",
                             reply_markup=save_announcement_kbd)
    else:
        await message.answer_photo(photo=f"{data['img']}",
                                   caption=f"{data['text']}",
                                   reply_markup=save_announcement_kbd)

    await state.set_state(CreateAnnouncement.final_check)


@admin_direct_router.message(StateFilter(CreateAnnouncement.final_check), F.text.lower() == "отправить всем")
async def send_announce(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await send_announcement(data['text'], data.get('img', ''))
    await message.answer("Анонс отправлен", reply_markup=admin_menu_kbd)
    await state.clear()


'''--------------------------------------создание мероприятия---------------------------------------------------'''


@admin_direct_router.message(StateFilter(None), F.text.lower() == "создать мероприятие", IsAdmin())
@admin_direct_router.message(StateFilter(CreateEvent.name), F.text.lower() == "назад")
async def choose_type(message: types.Message, state: FSMContext):
    await message.answer(
        "Создаем мероприятие! \n"
        "На каждом шаге для возврата к предыдущему пункту можешь написать \"Назад\".\n\n"
        "А сейчас выбери тип мероприятия",
        reply_markup=choose_type_kbd
    )
    await state.set_state(CreateEvent.type)


@admin_direct_router.message(StateFilter(CreateEvent.type), F.text.lower() == "платное")
@admin_direct_router.message(StateFilter(CreateEvent.name), F.text.lower() == "назад")
async def add_url(message: types.Message, state: FSMContext):
    if message.text.lower() != "назад":
        await state.update_data(type=message.text)
    await message.answer("Отправь ссылку с сайта на событие", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CreateEvent.url)


@admin_direct_router.message(StateFilter(CreateEvent.type), F.text.lower() == "бесплатное")
@admin_direct_router.message(StateFilter(CreateEvent.url), F.text)
@admin_direct_router.message(StateFilter(CreateEvent.description), F.text.lower() == "назад")
async def add_name(message: types.Message, state: FSMContext):
    if message.text.lower() == "бесплатное":
        await state.update_data(type=message.text)
    elif message.text.lower() != "назад":
        await state.update_data(url=message.text)
    await message.answer("Напиши название мероприятия", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CreateEvent.name)


@admin_direct_router.message(StateFilter(CreateEvent.name), F.text)
@admin_direct_router.message(StateFilter(CreateEvent.date), F.text.lower() == "назад")
async def add_description(message: types.Message, state: FSMContext):
    if message.text.lower() != "назад":
        await state.update_data(name=message.text)
    await message.answer("Напиши описание мероприятия")
    await state.set_state(CreateEvent.description)


@admin_direct_router.message(StateFilter(CreateEvent.description), F.text)
@admin_direct_router.message(StateFilter(CreateEvent.time), F.text.lower() == "назад")
async def add_date(message: types.Message, state: FSMContext):
    if message.text.lower() != "назад":
        await state.update_data(description=message.text)
    await message.answer("Напиши дату в формате ДД.ММ.ГГ")
    await state.set_state(CreateEvent.date)


@admin_direct_router.message(StateFilter(CreateEvent.date), F.text)
@admin_direct_router.message(StateFilter(CreateEvent.final_check), F.text.lower() == "назад")
async def add_time(message: types.Message, state: FSMContext):
    if message.text.lower() != "назад":
        try:
            ''' Не использовал strptime, т.к. она в конце дает дату вида гг.мм.дд. чч.мм.сс
            потом неудобно и некрасиво смотреть '''
            event_date = datetime.strptime(message.text, '%d.%m.%y')
            # day, month, year = map(int, message.text.split('.'))
            # await state.update_data(date=date(year, month, day))
            await state.update_data(date=event_date)
        except ValueError:
            await message.answer("Неверный формат! \nНапиши дату в формате ДД.ММ.ГГ")
        else:
            await message.answer("Напиши время в формате ЧЧ:ММ")
            await state.set_state(CreateEvent.time)

    else:
        await message.answer("Напиши время в формате ЧЧ:ММ")
        await state.set_state(CreateEvent.time)


@admin_direct_router.message(StateFilter(CreateEvent.time), F.text)
async def final(message: types.Message, state: FSMContext):
    try:
        event_time = datetime.strptime(message.text, '%H:%M')
        # hour, minute = map(int, message.text.split(':'))
        # await state.update_data(time=time(hour, minute))
        await state.update_data(time=time(event_time.hour, event_time.minute))
    except ValueError:
        await message.answer("Неверный формат! \nНапиши время в формате ЧЧ:ММ")
    else:
        data = await state.get_data()
        # todo: переписать красиво (сформировать строку заранее)
        if 'url' not in data:
            await message.answer(f"<b>{data['name']}</b>\n\n"
                                 f"{data['description']}\n\n"
                                 f"<u>когда:</u> {data['date'].day}.{data['date'].month}.{data['date'].year}, {data['time']}",
                                 reply_markup=save_event_kbd)
        else:
            await message.answer(f"<b>{data['name']}</b>\n\n"
                                 f"{data['description']}\n\n"
                                 f"<u>когда:</u> {data['date']}, {data['time']}\n\n"
                                 f"ссылка: {data['url']}", reply_markup=save_event_kbd)

        await state.set_state(CreateEvent.final_check)


@admin_direct_router.message(StateFilter(CreateEvent.final_check), F.text.lower() == "сохранить")
async def save_event(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        add_event(data)
    except SQLAlchemyError:
        await message.answer("Случилась ошибка, напиши Паше")
    else:
        #todo: Написать функцию, которая будет добавлять в планироващик отправку ссылки на мероприятие всем записавшимся
        await message.answer("Мероприятие добавлено", reply_markup=admin_menu_kbd)
        await state.clear()


'''--------------------------------------Функция для редактирования карточек-----------------------------------------'''


@admin_direct_router.message(StateFilter(None), F.text.lower() == "редактировать карточку", IsAdmin())
async def get_topic(message: types.Message, state: FSMContext):
    await message.answer(
        "Выбери тему, в которой находится карточка",
        reply_markup=make_catalogue()
    )
    await state.set_state(ChangeCard.choose_topic)


@admin_direct_router.message(StateFilter(ChangeCard.choose_topic), F.text.in_(create_topic_list()))
async def get_num(message: types.Message, state: FSMContext):
    topic = get_topic_by_title(message.text)
    await state.update_data(topic_id=topic.id, topic_last_num=topic.last_number)
    await message.answer(f"Напиши номер нужной карточки\n"
                         f"В этой теме их {topic.last_number}",
                         reply_markup=types.ReplyKeyboardRemove()
                         )
    await state.set_state(ChangeCard.choose_card)


@admin_direct_router.message(StateFilter(ChangeCard.choose_card), F.text)
async def choose_part(message: types.Message, state: FSMContext):
    topic = await state.get_data()
    try:
        if int(message.text) <= 0 or int(message.text) > topic['topic_last_num']:
            raise WrongLastNumber
    except ValueError:
        await message.answer("Напиши число!")
    except WrongLastNumber:
        await message.answer("Нет карточки с таким номером")
    else:
        card = await send_chosen_card(message.from_user.id, topic['topic_id'], int(message.text))
        await state.update_data(pic_url=card.url, pic_description=card.description, pic_num=card.position)
        await message.answer("Вот так выглядит карточка\n"
                             "Отправь мне картинку ИЛИ текст для замены")
        await state.set_state(ChangeCard.new_material)


@admin_direct_router.message(StateFilter(ChangeCard.new_material), F.text)
async def change_description(message: types.Message, state: FSMContext):
    await state.update_data(new_text=message.text)
    data = await state.get_data()
    await message.answer_photo(
        photo=data['pic_url'],
        caption=message.text,
        reply_markup=card_check
        )
    await state.set_state(ChangeCard.final_check)


@admin_direct_router.message(StateFilter(ChangeCard.new_material), F.photo)
async def change_picture(message: types.Message, state: FSMContext):
    await state.update_data(new_picture=message.photo[-1].file_id)
    data = await state.get_data()
    await message.answer_photo(
        photo=data['new_picture'],
        caption=data['pic_description'],
        reply_markup=card_check
        )
    await state.set_state(ChangeCard.final_check)


@admin_direct_router.message(StateFilter(ChangeCard.final_check), F.text.lower() == 'сохранить')
async def change_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_description = data['new_text'] if 'new_text' in data else data['pic_description']
    new_link = data['new_picture'] if 'new_picture' in data else data['pic_url']
    topic_id = data['topic_id']
    card_num = data['pic_num']
    change_card(topic_id, card_num, new_link, new_description)
    await message.answer("Карточка обновлена")
    await admin_menu(message, state)


'''--------------------------------------Функция для парса картинок-------------------------------------------------'''


@admin_direct_router.message(StateFilter(None), F.text.lower() == "обновить темы", IsAdmin())
async def refresh_topics(message: types.Message):
    await message.answer("парсим картинки")
    try:
        parse_topics()
    except SQLAlchemyError:
        await message.answer("Произошла ошибка лезь в логи")
    else:
        await message.answer("Темы, картинки обновлены")

