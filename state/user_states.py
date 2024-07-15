from aiogram.fsm.state import State, StatesGroup


class TopicChoose(StatesGroup):
    menu = State()
    catalogue = State()
    topic = State()
    change_topic = State()
    settings = State()
    # Добавить состояние приостановки подписки и изменения времени, либо сделать для них отдельную группу состояний


class BookingEvent(StatesGroup):
    catalogue = State()
    event = State()
