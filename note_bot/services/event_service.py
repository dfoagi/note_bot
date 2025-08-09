from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from datetime import datetime

from note_bot.models import Booking, Event, engine


def add_event(event_data):
    with Session(engine) as session:
        dt = datetime.combine(event_data['date'], event_data['time'])

        event = Event(
            is_free=bool(event_data['type']),
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


def check_booking(user_id, event_id):
    with Session(engine) as session:
        stmt = select(Booking).where(Booking.user_id == user_id).where(Booking.event_id == event_id)
        return session.scalars(stmt).first() is not None


def get_event(event_title, event_date):
    with Session(engine) as session:
        event_date = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S')
        stmt = select(Event).where(Event.title == event_title).where(Event.date == event_date)
        event: Event = session.scalars(stmt).first()
        return event


def create_events_list() -> list:
    with Session(engine) as session:
        # todo: в условии изменить время, в которое перестает показываться мероприятие (за 5/10/15 минут до начала)
        stmt = select(Event).where(Event.date > datetime.now())
        return list(session.scalars(stmt))
