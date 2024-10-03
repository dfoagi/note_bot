import os
from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    def __init__(self):
        self.admins = set(map(str, os.getenv('ADMINS').split(',')))

    async def __call__(self, message: Message):
        # print('i am being used')
        return str(message.from_user.username) in self.admins
