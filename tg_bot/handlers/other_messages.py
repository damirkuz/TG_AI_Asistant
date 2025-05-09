from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.keyboards import main_menu_keyboard
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']

from tg_bot.states import FSMMainMenu

router = Router()




@router.message()
async def process_other_messages(message: Message):
    await message.answer(LEXICON_ANSWERS_RU['other_messages'])