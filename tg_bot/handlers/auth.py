
from aiogram import Router
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient

from config_data import Config
from tg_bot.filters.correct_data import CorrectPhone, CorrectOTPCode, CorrectPassword
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.services import get_user_db
from tg_bot.services.redis_client_storage import RedisClientStorage
from tg_bot.states import FSMAuthState, FSMMainMenu
from tg_bot.keyboards import create_reply_kb, main_menu_keyboard, main_menu_admin_keyboard

from tg_bot.services.telethon_auth import auth_send_code, AuthStatesEnum, auth_enter_code, auth_enter_password
from tg_bot.services.database import save_auth, DB

__all__ = ['router', 'auth_request_phone']


router = Router()

router.message.filter(StateFilter(FSMAuthState))


@router.message(StateFilter(FSMAuthState.start_auth))
async def auth_request_phone(message: Message, state: FSMContext):
    button = KeyboardButton(
        text=LEXICON_BUTTONS_RU['share_phone'],
        request_contact=True)
    keyboard_now = create_reply_kb(button)
    await message.answer(text=LEXICON_ANSWERS_RU['auth_request_phone'], reply_markup=keyboard_now)
    await state.set_state(FSMAuthState.waiting_for_phone)


@router.message(StateFilter(FSMAuthState.waiting_for_phone), CorrectPhone())
async def auth_request_code(message: Message, state: FSMContext, phone: str, config: Config, redis_client_storage: RedisClientStorage):
    sent_result: dict[str, TelegramClient | str] | AuthStatesEnum = await auth_send_code(config.tg_app, str(message.from_user.id), phone)
    if sent_result == AuthStatesEnum.PhoneNumberBanned:
        await message.answer(text=LEXICON_ANSWERS_RU['auth_banned_phone'])
        return
    else:
        # сохраняем сессию в локальное хранилище
        session_string = sent_result.get("session_string")
        tg_client = sent_result.get("tg_client")
        state_data = await state.get_data()
        bot_user_id = state_data.get('bot_user_id')
        await redis_client_storage.save_session(bot_user_id, tg_client)

        await state.update_data(session_string=session_string, phone=phone)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_request_code'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMAuthState.waiting_for_code)


@router.message(StateFilter(FSMAuthState.waiting_for_phone))
async def auth_incorrect_phone(message: Message):
    await message.answer(text=LEXICON_ANSWERS_RU['auth_incorrect_phone'])


@router.message(StateFilter(FSMAuthState.waiting_for_code), CorrectOTPCode())
async def auth_process_code(message: Message, state: FSMContext, code: str, db: DB, redis_client_storage: RedisClientStorage, config: Config):
    state_data = await state.get_data()
    bot_user_id = state_data.get('bot_user_id')
    client = await redis_client_storage.get_client(
        user_id=bot_user_id,
        api_id=config.tg_app.api_id,
        api_hash=config.tg_app.api_hash
    )
    phone = state_data.get("phone")
    result = await auth_enter_code(client=client, phone=phone, code=code)
    match result:
        case AuthStatesEnum.CodeValid:
            await end_auth(message=message, state=state, client=client, db=db)
            return
        case AuthStatesEnum.CodeInvalid:
            await message.answer(text=LEXICON_ANSWERS_RU['auth_invalid_code'])
            return
        case AuthStatesEnum.CodeExpired:
            await message.answer(text=LEXICON_ANSWERS_RU['auth_expired_code'])
            await auth_request_code(message=message, state=state, phone=phone)
            return
        case AuthStatesEnum.PasswordNeeded:
            await message.answer(text=LEXICON_ANSWERS_RU['auth_need_password'])
            await state.set_state(FSMAuthState.waiting_for_password)


@router.message(StateFilter(FSMAuthState.waiting_for_code))
async def auth_process_incorrect_code(message: Message):
    await message.answer(text=LEXICON_ANSWERS_RU['auth_message_incorrect_code'])


@router.message(StateFilter(FSMAuthState.waiting_for_password),
                CorrectPassword())
async def auth_process_code(
        message: Message,
        state: FSMContext,
        password: str,
        db: DB,
        redis_client_storage: RedisClientStorage,
        config: Config):
    state_data = await state.get_data()
    await message.delete()
    bot_user_id = state_data.get('bot_user_id')
    client = await redis_client_storage.get_client(
        user_id=bot_user_id,
        api_id=config.tg_app.api_id,
        api_hash=config.tg_app.api_hash
    )

    result = await auth_enter_password(client=client, password=password)
    match result:
        case AuthStatesEnum.PasswordValid:
            await end_auth(message=message, state=state, client=client, db=db, password=password)
            return
        case AuthStatesEnum.PasswordInvalid:
            await message.answer(text=LEXICON_ANSWERS_RU['auth_invalid_password'])


async def end_auth(
        message: Message,
        state: FSMContext,
        client: TelegramClient,
        db: DB,
        password: str = None):
    session_string = client.session.save()
    state_data = await state.get_data()
    await save_auth(db=db, client=client, session_string=session_string, password=password, bot_user_id=state_data.get('bot_user_id'))
    user_db = await get_user_db(message.from_user.id)
    if user_db.is_admin:
        await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'], reply_markup=main_menu_admin_keyboard)
    else:
        await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)
