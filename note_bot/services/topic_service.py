from sqlalchemy.orm import Session

from note_bot.models import Card, Topic, engine
from sqlalchemy import select


def create_active_topic_list() -> list:
    with Session(engine) as session:
        stmt = select(Topic.title).where(Topic.is_active)
        return list(session.scalars(stmt))


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


def get_topic_by_title(topic_title):
    with Session(engine) as session:
        stmt = select(Topic).where(Topic.title == topic_title)
        topic: Topic = session.scalars(stmt).first()
        return topic


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

