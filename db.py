from sqlalchemy import create_engine, text, Table, MetaData, Column, Integer, String, update, Time
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine("postgresql+psycopg://postgres:251415Aa@localhost/pictures", echo=True)
engine.connect()

metadata = MetaData()

pics_table = Table(
    'pictures',
    metadata,
    Column('pic_id', Integer),
    Column('tg_id', String),
    Column('folder', String),
    Column('text', String)
)

users_table = Table(
    'followers',
    metadata,
    Column('user_id', Integer),
    Column('send_time', Integer)
)

session = sessionmaker(engine)


def get_pic():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM pictures ORDER BY RANDOM() LIMIT 1;"))
        row = res.one()

    return row


def add_tg_id(pic_id, new_tg_id):
    stmt = update(pics_table).where(pics_table.c['pic_id'] == pic_id).values(tg_id=f'{new_tg_id}')
    with Session(engine) as sess:
        sess.execute(stmt)
        sess.commit()


def get_users_for_daily_send():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM followers"))
        print(res.one())


def check_registration(user_id):
    with engine.connect() as conn:
        res = conn.execute(text(f"SELECT EXISTS(SELECT * FROM followers WHERE user_id = {user_id})")).one()[0]

    return res


def check_cur_subscription(user_id):
    pass


# 'AgACAgIAAxkDAAIDPWXt0_9rIhDRbUlY3EDQkyg-lKClAAIr1zEbzrpxS2DfeXgvMz6OAQADAgADdwADNAQ'
