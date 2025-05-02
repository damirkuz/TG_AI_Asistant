from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.keyboards import main_menu_keyboard
from tg_bot.states import FSMMainMenu

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']


router = Router()

@router.message(F.text == LEXICON_BUTTONS_RU['back_to_main_menu'])
async def process_accept_rules(message: Message, state: FSMContext):
    await message.answer(LEXICON_ANSWERS_RU['back_to_main_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)