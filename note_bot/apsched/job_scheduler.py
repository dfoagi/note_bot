from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from note_bot.models import engine, async_send_cards


async def scheduler_start(send_freq=5):
    job_store = SQLAlchemyJobStore(
        engine=engine,
        tablename='schedule')
    scheduler = AsyncIOScheduler()
    scheduler.add_jobstore(jobstore=job_store)
    if scheduler.get_job('aio_cards_sending') is None:
        scheduler.add_job(
            async_send_cards,
            'interval',
            id='aio_cards_sending',
            minutes=send_freq,
            start_date='2024-09-12 15:10:05')
    scheduler.start()
