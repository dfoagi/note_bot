from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, time
from note_bot.models import User, Topic, Progress, UsersAnswers, engine


def register_user(user_id):
    with Session(engine) as session:
        user = User(
            tg_id=user_id,
        )
        session.add(user)
        session.commit()


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


def change_subscription_time(user_id, new_time):
    with Session(engine) as session:
        stmt = select(User).where(User.tg_id == user_id)
        user: User = session.scalars(stmt).one()
        user.time = new_time
        session.commit()


def check_subscription(user_id):
    with Session(engine) as session:
        stmt = select(User.cur_subscription).where(User.tg_id == user_id)
        return session.scalars(stmt).first() > 0


def check_registration(user_id):
    with Session(engine) as session:
        stmt = select(UsersAnswers.user_id).where(UsersAnswers.user_id == user_id)
        return session.scalars(stmt).first() is not None


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
