from sqlalchemy import create_engine, func, Time, MetaData, Table, Column, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import datetime, time


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    cur_subscription: Mapped[int] = mapped_column(default=0)
    time: Mapped[time] = mapped_column(Time, default=func.now())
    last_pic_day: Mapped[datetime] = mapped_column(nullable=True)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    type: Mapped[int]
    date: Mapped[datetime]
    spaces: Mapped[int]


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    last_number: Mapped[int]


# Декларативно не разрешает создавать алхимия т.к. нет первичного ключа. Поэтому создаем императивно

pics_table = Table(
    'cards',
    Base.metadata,
    Column('topic', Integer),
    Column('position', Integer),
    Column('path', String),
    Column('description', String),
    Column('url', String)
)

progress = Table(
    'progress',
    Base.metadata,
    Column('user_id', Integer),
    Column('topic_id', Integer),
    Column('card_number', Integer)
)

bookings = Table(
    'bookings',
    Base.metadata,
    Column('event_id', Integer),
    Column('user_id', Integer)
)

engine = create_engine("postgresql+psycopg://postgres:251415Aa@localhost/pictures", echo=True)

# Создать все таблички
# Base.metadata.create_all(engine)

# Добавить пользователя
# with Session(engine) as session:
#     paul = User(
#         tg_id=592386558,
#         time=datetime.now()
#     )
#     session.add(paul)
#     session.commit()


# Добавить темы
# with Session(engine) as session:
#     topic1 = Topic(
#         title="Тема 1. Дом и семья",
#         last_number=30
#     )
#     topic2 = Topic(
#         title="Тема 2. Здоровье",
#         last_number=30
#     )
#     topic3 = Topic(
#         title="Тема 3. Музыка и танцы",
#         last_number=28
#     )
#
#     session.add(topic1)
#     session.add(topic2)
#     session.add(topic3)
#     session.commit()

# session = Session(engine)
# stmt = select(Topic.title)
# print(list(session.scalars(stmt)))


# for i in session.scalars(stmt):
#     print(i)

def create_topic_list() -> list:
    session = Session(engine)
    stmt = select(Topic.title)
    return list(session.scalars(stmt))


def change_user_subscription(user_id, topic):
    session = Session(engine)
    stmt = select(User).where(User.tg_id == user_id)
    user = session.scalars(stmt).one()
    user.cur_subscription = topic
    session.commit()
