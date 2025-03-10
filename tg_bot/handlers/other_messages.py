from aiogram import Router
from aiogram.types import Message
from tg_bot.lexicon import LEXICON_ANSWERS_RU

__all__ = ['router']

router = Router()


@router.message()
async def process_other_messages(message: Message):
    await message.answer(LEXICON_ANSWERS_RU['other_messages'])