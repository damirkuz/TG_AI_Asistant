from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils import keyboard
from tg_bot.keyboards import create_inline_kb, create_reply_kb

from tg_bot.lexicon import LEXICON_ANSWERS_RU

__all__ = ['router']

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    keyboard_now = create_reply_kb('register')
    await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=keyboard_now)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON_ANSWERS_RU['/help'])
