from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    question_1 = State()
    question_2 = State()


class TopicChoose(StatesGroup):
    menu = State()
    catalogue = State()
    topic = State()
    change_topic = State()
    last_check = State()
    settings = State()
    ask_time = State()
    change_time = State()
    pause_subscription = State()


class BookingEvent(StatesGroup):
    catalogue = State()
    event = State()
    choice = State()


class CreateAnnouncement(StatesGroup):
    text = State()
    picture = State()
    final_check = State()
    send_announcement = State()


class CreateEvent(StatesGroup):
    type = State()
    url = State()
    name = State()
    description = State()
    date = State()
    time = State()
    final_check = State()


class ChangeCard(StatesGroup):
    choose_topic = State()
    choose_card = State()
    choose_part = State()
    new_material = State()
    new_pic = State()
    new_text = State()
    final_check = State()
