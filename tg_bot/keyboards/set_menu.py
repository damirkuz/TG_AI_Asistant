from aiogram import Bot
from aiogram.types import BotCommand
from tg_bot.lexicon import LEXICON_COMMANDS_RU

__all__ = ['set_main_menu']

# Функция для настройки кнопки Menu бота


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in LEXICON_COMMANDS_RU.items()
    ]
    await bot.set_my_commands(main_menu_commands)
