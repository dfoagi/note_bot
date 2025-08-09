from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='main_menu',
            description='Перейти в главное меню'
        ),
        BotCommand(
            command='help',
            description='Прочитать описание'
        ),
        BotCommand(
            command='get_card',
            description='Получить карточку'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
