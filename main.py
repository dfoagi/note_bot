import argparse
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

from note_bot.utils.commands import set_commands
from note_bot.handlers.user_direct import user_direct_router
from note_bot.handlers.admin_direct import admin_direct_router
from note_bot.apsched.job_scheduler import scheduler_start

load_dotenv()
parser = argparse.ArgumentParser(prog='note_self_bot', description='Telegram bot that will allow users to '
                                                                   'get cards and book events')
parser.add_argument('--freq',
                    type=int,
                    default=5,
                    help='The frequency with which the dispatch will be sent')

API_TOKEN = os.getenv('TOKEN')

logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp: Dispatcher = Dispatcher()
dp.include_routers(admin_direct_router, user_direct_router)


async def main(send_freq):
    await set_commands(bot)
    await scheduler_start(send_freq)

    await dp.start_polling(bot)

args = parser.parse_args()

if __name__ == '__main__':
    asyncio.run(main(args.freq))
