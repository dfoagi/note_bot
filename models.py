import os
import logging
from sqlalchemy import create_engine, Time, select, extract, ForeignKey, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime, time
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    cur_subscription: Mapped[int] = mapped_column(default=0)
    time: Mapped[time] = mapped_column(Time, nullable=True)
    last_pic_day: Mapped[datetime] = mapped_column(nullable=True)

    # booked_events: Mapped[list["Event"]] = relationship(
    #     secondary="bookings",
    #     back_populates="id"
    # )
    #
    # sub_title: Mapped["Topic"] = relationship(back_populates='id')


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]  # Насколько неприятно, если хранить тип не в числе а строкой?
    title: Mapped[str]
    description: Mapped[str]
    date: Mapped[datetime]
    spaces: Mapped[int] = mapped_column(default=10)
    url: Mapped[str]

    # listeners: Mapped[list["User"]] = relationship(
    #     secondary="bookings",
    #     back_populates="tg_id"
    # )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    last_number: Mapped[int]


class Card(Base):
    __tablename__ = "cards"

    topic: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str]
    description: Mapped[str]
    url: Mapped[str] = mapped_column(nullable=True)


class Progress(Base):
    __tablename__ = "progress"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id"),
        primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        primary_key=True)
    card_number: Mapped[int]


class Booking(Base):
    __tablename__ = "bookings"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id"),
        primary_key=True)


class UsersAnswers(Base):
    __tablename__ = "answers"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    tg_username: Mapped[str]
    name: Mapped[str]
    question1: Mapped[str]
    question2: Mapped[str]


load_dotenv()
logger = logging.getLogger("Logger")
engine_url = os.getenv('DB_URL')
API_TOKEN = os.getenv('TOKEN')
admin = os.getenv('MAIN_ADMIN')

engine = create_engine(engine_url, echo=False)
bot: Bot = Bot(token=API_TOKEN)


# Создать таблички
# Base.metadata.create_all(engine)


def create_topic_list() -> list:
    with Session(engine) as session:
        stmt = select(Topic.title)
        return list(session.scalars(stmt))


def create_events_list() -> list:
    with Session(engine) as session:
        # todo: в условии изменить время, в которое перестает показываться мероприятие (за 5/10/15 минут до начала)
        stmt = select(Event).where(Event.date > datetime.now())
        return list(session.scalars(stmt))


def get_user_list() -> list:
    with Session(engine) as session:
        stmt = select(User.tg_id)
        return list(session.scalars(stmt))


# todo: переделать эти запросы через джоины
def get_user_time_topic(user_id) -> [User.time, Topic.title]:
    with Session(engine) as session:
        stmt = select(User).where(User.tg_id == user_id)
        user: User = session.scalars(stmt).first()
        if user.cur_subscription == 0:
            return [user.time, 0, 0]
        topic: Topic = session.scalars(select(Topic).where(Topic.id == user.cur_subscription)).first()
        progress: Progress = session.scalars(select(Progress.card_number).where(
            Progress.user_id == user_id).where(Progress.topic_id == user.cur_subscription)).first()
        return [user.time, topic.title, [progress, topic.last_number]]


def register_user(user_id):
    with Session(engine) as session:
        user = User(
            tg_id=user_id,
        )
        session.add(user)
        session.commit()


def register_answers(user_id, tg_username, user_name, q1, q2):
    with Session(engine) as session:
        row = UsersAnswers(
            user_id=user_id,
            tg_username=tg_username,
            name=user_name,
            question1=q1,
            question2=q2
        )
        session.add(row)
        session.commit()


async def send_announcement(text: str, image):
    user_list = get_user_list()
    for user in user_list:
        try:
            if image:
                await bot.send_photo(
                    chat_id=user,
                    photo=image,
                    caption=text)
            else:
                await bot.send_message(
                    chat_id=user,
                    text=text)
        except TelegramBadRequest:
            await bot.send_message(chat_id=admin, text=f'У этого id: {user} ошибка')


def change_user_subscription(user_id, topic: int):
    session = Session(engine)
    stmt = select(User).where(User.tg_id == user_id)
    user: User = session.scalars(stmt).one()
    if not user.time:
        cur_time = datetime.now()
        cur_minute, cur_hour = cur_time.minute, cur_time.hour
        if cur_minute % 5 in (0, 1, 2, 3):
            cur_minute = (cur_minute // 5) * 5 + 5
        else:
            cur_minute = (cur_minute // 5) * 5 + 10
        if cur_minute > 59:
            cur_minute %= 60
            cur_hour += 1
            if cur_hour > 23:
                cur_hour %= 24
        user.time = time(cur_hour, cur_minute)

    have_progress = session.scalars(
        select(Progress.card_number).where(Progress.user_id == user_id).where(Progress.topic_id == topic)
    ).first()

    if have_progress is None:
        cur_progress = Progress(
            user_id=user_id,
            topic_id=topic,
            card_number=0
        )
        session.add(cur_progress)

    user.cur_subscription = topic
    session.commit()
    session.close()


def add_topic(topic_id: int, topic_title: str, desc: str, n: int):
    with Session(engine) as session:
        topic = Topic(
            id=topic_id,
            title=topic_title,
            description=desc,
            last_number=n
        )
        session.add(topic)
        session.commit()


def add_card(topic_id, pos, path, desc):
    with Session(engine) as session:
        card = Card(
            topic=topic_id,
            position=pos,
            path=path,
            description=desc
        )
        session.add(card)
        session.commit()


def add_event(event_data):
    with Session(engine) as session:
        dt = datetime.combine(event_data['date'], event_data['time'])

        event = Event(
            type=event_data['type'],
            title=event_data['name'],
            description=event_data['description'],
            date=dt,
            url=event_data['url'] if 'url' in event_data else ""
        )
        session.add(event)
        session.commit()


def add_booking(event_id, user_id):
    with Session(engine) as session:
        booking = Booking(
            user_id=user_id,
            event_id=event_id
        )
        session.add(booking)
        session.commit()


def delete_booking(event_id, user_id):
    with Session(engine) as session:
        stmt = delete(Booking).where(Booking.user_id == user_id).where(Booking.event_id == event_id)
        session.execute(stmt)
        session.commit()


async def send_chosen_card(user_id, topic_id, card_number):
    with Session(engine) as session:
        card: Card = session.scalars(
            select(Card).where(Card.topic == topic_id).where(Card.position == card_number)).first()
        if card.url is None:
            msg = await bot.send_photo(
                chat_id=user_id,
                photo=FSInputFile(card.path),
                caption=str(card.description).replace('\\n', '\n')
            )
            card.url = msg.photo[-1].file_id
            session.commit()
        else:
            await bot.send_photo(
                chat_id=user_id,
                photo=str(card.url),
                caption=str(card.description).replace('\\n', '\n')
            )
        return card


def get_topic_by_title(topic_title):
    with Session(engine) as session:
        stmt = select(Topic).where(Topic.title == topic_title)
        topic: Topic = session.scalars(stmt).first()
        return topic


def get_event(event_title, event_date):
    with Session(engine) as session:
        event_date = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S')
        stmt = select(Event).where(Event.title == event_title).where(Event.date == event_date)
        event: Event = session.scalars(stmt).first()
        return event


def check_subscription(user_id):
    with Session(engine) as session:
        stmt = select(User.cur_subscription).where(User.tg_id == user_id)
        return session.scalars(stmt).first() > 0


def check_registration(user_id):
    with Session(engine) as session:
        stmt = select(UsersAnswers.user_id).where(UsersAnswers.user_id == user_id)
        return session.scalars(stmt).first() is not None


def check_booking(user_id, event_id):
    with Session(engine) as session:
        stmt = select(Booking).where(Booking.user_id == user_id).where(Booking.event_id == event_id)
        return session.scalars(stmt).first() is not None


def change_subscription_time(user_id, new_time):
    with Session(engine) as session:
        stmt = select(User).where(User.tg_id == user_id)
        user: User = session.scalars(stmt).one()
        user.time = new_time
        session.commit()


def cancel_subscription(user_id):
    session = Session(engine)
    stmt = select(User).where(User.tg_id == user_id)
    user: User = session.scalars(stmt).one()
    if user.cur_subscription == 0:
        return False
    user.cur_subscription = 0
    session.commit()
    session.close()
    return True


def get_topics_ids():  # используется при добавлении новых тем только
    with Session(engine) as session:
        stmt = select(Topic.id)
        return list(session.scalars(stmt))


# todo: поменять на апдейт
def change_card(topic_id, card_number, new_img, new_desc):
    with Session(engine) as session:
        card: Card = session.scalars(
            select(Card).where(Card.topic == topic_id).where(Card.position == card_number)).first()
        card.url = new_img
        card.description = new_desc
        session.commit()


async def async_send_cards():
    with Session(engine) as session:
        # stmt = select(User).where(User.cur_subscription > 0).where(extract('HOUR', User.time) == datetime.now().hour). \
        #     where(extract('MINUTE', User.time) == datetime.now().minute)
        users = session.scalars(select(User).where(User.cur_subscription > 0))
        for user in users:
            # if user.last_pic_day and user.last_pic_day.day == datetime.now().day:
            #     continue
            progress: Progress = session.scalars(
                select(Progress).where(Progress.user_id == user.tg_id).where(Progress.topic_id == user.cur_subscription)
            ).first()
            topic: Topic = session.scalars(select(Topic).where(Topic.id == user.cur_subscription)).first()
            card: Card = session.scalars(
                select(Card).where(Card.topic == user.cur_subscription).where(
                    Card.position == progress.card_number + 1)).first()
            logger.info(card.url)
            if card.url is None:
                msg = await bot.send_photo(
                    chat_id=user.tg_id,
                    photo=FSInputFile(card.path),
                    caption=str(card.description).replace('\\n', '\n')
                )
                card.url = msg.photo[-1].file_id
            else:
                await bot.send_photo(
                    chat_id=user.tg_id,
                    photo=str(card.url),
                    caption=str(card.description).replace('\\n', '\n')
                )
            user.last_pic_day = datetime.now()
            progress.card_number += 1
            if progress.card_number == topic.last_number:
                await bot.send_message(chat_id=user.tg_id,
                                       text='Это была последняя картинка по данной теме. Поздравляем с прохождением\n\n'
                                            'Выбрать новую тему можно в каталоге тем')
                progress.card_number = 0
                user.cur_subscription = 0
            session.commit()
