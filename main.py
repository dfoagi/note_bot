import asyncio
import logging
import os

import aiogram.types
from aiogram import Bot, Dispatcher, F
from dotenv import load_dotenv

from utils.commands import set_commands
from handlers.user_direct import user_direct_router

load_dotenv()

API_TOKEN = os.getenv('TOKEN')

logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()
dp.include_router(user_direct_router)


@dp.message(F.photo)
async def get_file_id(message):
    photo_id = message.photo[-1].file_id
    print(photo_id)
    # await message.answer_photo(photo=f'{photo_id}')


async def main():
    await set_commands(bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
