import os
import logging
from typing import Optional
from sqlalchemy import create_engine, Time, ForeignKey, inspect, Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, time
from dotenv import load_dotenv
from aiogram import Bot


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    cur_subscription_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.id"), nullable=True)
    time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    last_pic_day: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    cur_subscription: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="users")
    progress: Mapped[list["Progress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str]
    last_number: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    users: Mapped[list["User"]] = relationship(back_populates="cur_subscription")
    cards: Mapped[list["Card"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    progresses: Mapped[list["Progress"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str]
    description: Mapped[str]
    url: Mapped[Optional[str]] = mapped_column(nullable=True)

    topic: Mapped["Topic"] = relationship(back_populates="cards")


class Progress(Base):
    __tablename__ = "progress"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), primary_key=True)
    card_number: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="progress")
    topic: Mapped["Topic"] = relationship(back_populates="progresses")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    title: Mapped[str]
    description: Mapped[str]
    date: Mapped[datetime]
    spaces: Mapped[int] = mapped_column(default=10)
    url: Mapped[str]

    bookings: Mapped[list["Booking"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), primary_key=True)

    event: Mapped["Event"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship(back_populates="bookings")


class UsersAnswers(Base):
    __tablename__ = "answers"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), primary_key=True)
    tg_username: Mapped[str]
    name: Mapped[str]
    question1: Mapped[str]
    question2: Mapped[str]


load_dotenv()
logger = logging.getLogger("Logger")
engine_url = os.getenv('DB_URL')
API_TOKEN = os.getenv('TOKEN')

engine = create_engine(engine_url, pool_pre_ping=True, echo=False)
bot: Bot = Bot(token=API_TOKEN)


# Создать таблички
def create_tables():
    table_names = inspect(engine).get_table_names()
    print(table_names)
    if len(table_names) < 2:
        Base.metadata.create_all(engine)


create_tables()
