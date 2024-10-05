from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from note_bot.models import engine, async_send_cards


async def scheduler_start():
    job_store = SQLAlchemyJobStore(
        engine=engine,
        tablename='schedule')
    scheduler = AsyncIOScheduler()
    scheduler.add_jobstore(jobstore=job_store)
    # todo: добавить функию проверки наличия работы с таким id; изменить интервал, время начала
    # scheduler.add_job(async_send_cards, 'interval', id='aio_cards_sending', minutes=5, start_date='2024-09-12 15:10:05')
    scheduler.start()
