import os
from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):

    def __init__(self):
        self.admins = self._load_admins()

    def _load_admins(self) -> set[str]:
        """
        Method retrieves __admins__ list from env variable ADMINS.
        This variable has strict format: telegram user logins and ids separated by comma

        Returns unique admins (names and ids)
        """
        admins_string = os.getenv('ADMINS')
        admin_logins = map(str, admins_string.split(','))
        unique_admins = set(admin_logins)
        return unique_admins

    async def __call__(self, message: Message):
        return str(message.from_user.username) in self.admins
