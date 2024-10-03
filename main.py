import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

from utils.commands import set_commands
from handlers.user_direct import user_direct_router
from handlers.admin_direct import admin_direct_router
from apsched.job_scheduler import scheduler_start

load_dotenv()

API_TOKEN = os.getenv('TOKEN')

logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp: Dispatcher = Dispatcher()
dp.include_routers(admin_direct_router, user_direct_router)


async def main():
    await set_commands(bot)
    await scheduler_start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
