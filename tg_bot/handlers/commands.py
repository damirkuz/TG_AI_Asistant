from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from tg_bot.filters import IsRegistered
from tg_bot.keyboards import create_reply_kb, main_menu_keyboard, settings_add_telegram_keyboard
from tg_bot.services.database import DB
from tg_bot.services.database.db_functions import save_bot_user
from tg_bot.states import FSMRulesAgreement, FSMMainMenu, FSMSettingsState

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']


router = Router()


@router.message(CommandStart(), IsRegistered())
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)


# сюда попадёт новый пользователь
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    keyboard_now = create_reply_kb('accept_rules')
    await message.answer(text=LEXICON_ANSWERS_RU['/start'])
    await message.answer(text=LEXICON_ANSWERS_RU['agree_rules'], reply_markup=keyboard_now, parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(FSMRulesAgreement.waiting_for_agree)


# согласие с правилами реализую здесь, так как это единичная операция и
# логично оставить её там, где вызывается.
@router.message(StateFilter(FSMRulesAgreement.waiting_for_agree),
                F.text == LEXICON_BUTTONS_RU['accept_rules'])
async def process_accept_rules(message: Message, state: FSMContext, db: DB):
    await message.answer(text=LEXICON_ANSWERS_RU['accept_success'])
    # сохраняем пользователя в бд
    bot_user_id = await save_bot_user(db=db, telegram_id=message.from_user.id, full_name=message.from_user.full_name, username=message.from_user.username)
    await state.update_data(bot_user_id=bot_user_id)
    await state.set_state(FSMSettingsState.waiting_choice)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_menu'], reply_markup=settings_add_telegram_keyboard)




# запустится, если пользователь не принял правила
@router.message(StateFilter(FSMRulesAgreement.waiting_for_agree))
async def process_accept_rules(message: Message):
    keyboard_now = create_reply_kb('accept_rules')
    await message.answer(text=LEXICON_ANSWERS_RU['accept_retry'], reply_markup=keyboard_now)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON_ANSWERS_RU['/help'])
