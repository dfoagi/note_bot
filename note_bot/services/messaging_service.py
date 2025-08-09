import asyncio
from datetime import datetime
import os
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile
from sqlalchemy import select, extract
from sqlalchemy.orm import Session

from note_bot.services.user_service import get_user_list
from note_bot.models import bot, engine, logger, Card, Progress, Topic, User
from config import ADMIN_ID, RATE_LIMIT


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
            await asyncio.sleep(1 / RATE_LIMIT)  # Чтобы не отправлялось больше *rate_limit* сообщений в секунду
        except TelegramBadRequest:
            await bot.send_message(chat_id=ADMIN_ID, text=f'У этого id: {user} ошибка')


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


async def async_send_cards():
    with Session(engine) as session:
        stmt = select(User).where(User.cur_subscription > 0).where(extract('HOUR', User.time) == datetime.now().hour). \
            where(extract('MINUTE', User.time) == datetime.now().minute)
        users = session.scalars(stmt)
        for user in users:
            if user.last_pic_day and user.last_pic_day.day == datetime.now().day:
                continue
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
            await asyncio.sleep(1 / RATE_LIMIT)
            if progress.card_number == topic.last_number:
                await bot.send_message(chat_id=user.tg_id,
                                       text='Это была последняя картинка по данной теме. Поздравляем с прохождением\n\n'
                                            'Выбрать новую тему можно в каталоге тем')
                progress.card_number = 0
                user.cur_subscription = 0
            session.commit()


async def send_extra_card(user_id):
    with Session(engine) as session:
        stmt = select(User).where(User.tg_id == user_id)
        user: User = session.scalars(stmt).first()
        if user.cur_subscription == 0:
            await bot.send_message(user_id,
                                   "Вы не подписаны на тему"
                                   )

        elif user.last_pic_day and user.last_pic_day.day == datetime.now().day:
            await bot.send_message(user_id,
                                   "Вы пока не можете воспользоваться данной функцией"
                                   )
        else:
            progress: Progress = session.scalars(
                select(Progress).where(Progress.user_id == user.tg_id).where(Progress.topic_id == user.cur_subscription)
            ).first()
            topic: Topic = session.scalars(select(Topic).where(Topic.id == user.cur_subscription)).first()
            card: Card = session.scalars(select(Card).where(Card.topic == user.cur_subscription).where(
                Card.position == progress.card_number + 1)).first()

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
