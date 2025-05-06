from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import StateFilter
from telethon import TelegramClient

from tg_bot.handlers.auth import auth_request_phone
from tg_bot.keyboards.reply_keyboards import settings_add_telegram_keyboard, main_menu_keyboard, \
    main_menu_admin_keyboard
from tg_bot.services import get_user_db
from tg_bot.services.database import save_auth, DB
from tg_bot.states import FSMSettingsState, FSMMainMenu, FSMAuthState
from tg_bot.filters import IsCorrectSession

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']


router = Router()

router.message.filter(StateFilter(FSMSettingsState))


@router.message(F.text == LEXICON_BUTTONS_RU['settings_add_telegram'])
async def add_telegram(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_menu'], reply_markup=settings_add_telegram_keyboard)


# авторизация по сессии
@router.message(F.text == LEXICON_BUTTONS_RU['settings_add_telegram_session'])
async def add_telegram_session(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_session'])
    await state.set_state(FSMSettingsState.waiting_session_file)


@router.message(StateFilter(FSMSettingsState.waiting_session_file), IsCorrectSession())
async def waiting_session_file(message: Message, state: FSMContext, client: TelegramClient, session_string: str, db: DB):
    state_data = await state.get_data()
    await save_auth(client=client, db=db, session_string=session_string, bot_user_id=state_data.get('bot_user_id'))
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_session_good'])
    user_db = await get_user_db(message.from_user.id)
    if user_db.is_admin:
        await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_admin_keyboard)
    else:
        await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)


# сюда попадёт если неправильный session файл
@router.message(StateFilter(FSMSettingsState.waiting_session_file))
async def waiting_session_file(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_session_bad'])


# авторизация по телефону
@router.message(F.text == LEXICON_BUTTONS_RU['settings_add_telegram_phone'])
async def add_telegram_session(message: Message, state: FSMContext):
    await state.set_state(FSMAuthState.start_auth)
    await auth_request_phone(message=message, state=state)