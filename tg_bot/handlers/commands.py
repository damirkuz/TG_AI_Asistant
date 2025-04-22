from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils import keyboard
from tg_bot.filters import IsRegistered
from tg_bot.handlers.auth import auth_request_phone
from tg_bot.keyboards import create_inline_kb, create_reply_kb, main_menu_keyboard
from tg_bot.states import FSMMainState, FSMAuthState

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']


router = Router()


@router.message(CommandStart(), IsRegistered())
async def process_start_command(message: Message, state: FSMContext):
    keyboard_now = main_menu_keyboard
    await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=keyboard_now)
    await state.set_state(FSMMainState.main_menu)


# сюда попадёт новый пользователь
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    keyboard_now = create_reply_kb('accept_rules')
    await message.answer(text=LEXICON_ANSWERS_RU['/start'])
    await message.answer(text=LEXICON_ANSWERS_RU['agree_rules'], reply_markup=keyboard_now, parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(FSMMainState.waiting_rules_accept)


# согласие с правилами реализую здесь, так как это единичная операция и
# логично оставить её там, где она вызывается
@router.message(StateFilter(FSMMainState.waiting_rules_accept),
                F.text == LEXICON_BUTTONS_RU['accept_rules'])
async def process_accept_rules(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['accept_success'])
    await state.set_state(FSMAuthState.start_auth)
    await auth_request_phone(message=message, state=state)


# запустится, если пользователь не принял правила
@router.message(StateFilter(FSMMainState.waiting_rules_accept))
async def process_accept_rules(message: Message, state: FSMContext):
    keyboard_now = create_reply_kb('accept_rules')
    await message.answer(text=LEXICON_ANSWERS_RU['accept_retry'], reply_markup=keyboard_now)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON_ANSWERS_RU['/help'])
