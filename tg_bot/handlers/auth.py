
from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from asyncpg import Pool
from telethon import TelegramClient

from tg_bot.filters.correct_data import CorrectPhone, CorrectOTPCode, CorrectPassword
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.states import FSMAuthState
from tg_bot.keyboards import create_reply_kb

from telegram_actions import auth_send_code, AuthStatesEnum, auth_enter_code, auth_enter_password
from database import save_auth

__all__ = ['router']


router = Router()


@router.message(StateFilter(FSMAuthState.start_auth))
async def auth_request_phone(message: Message, state: FSMContext):
    button = KeyboardButton(
        text=LEXICON_BUTTONS_RU['share_phone'],
        request_contact=True)
    keyboard_now = create_reply_kb(button)
    await message.answer(text=LEXICON_ANSWERS_RU['auth_request_phone'], reply_markup=keyboard_now)
    await state.set_state(FSMAuthState.waiting_for_phone)


@router.message(StateFilter(FSMAuthState.waiting_for_phone), CorrectPhone())
async def auth_request_code(message: Message, state: FSMContext, phone: str):
    config = router.parent_router.workflow_data.get("config")
    sent_result: dict[str, TelegramClient | str] | AuthStatesEnum = await auth_send_code(config.tg_app, str(message.from_user.id), phone)
    if sent_result == AuthStatesEnum.PhoneNumberBanned:
        await message.answer(text=LEXICON_ANSWERS_RU['auth_banned_phone'])
        return
    else:
        session_path = sent_result.get("session_path")
        router.parent_router.workflow_data.update({"tg_client": sent_result.get("tg_client")})
        await state.update_data(session_path=session_path)
        await state.update_data(phone=phone)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_request_code'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMAuthState.waiting_for_code)


@router.message(StateFilter(FSMAuthState.waiting_for_phone))
async def auth_incorrect_phone(message: Message):
    await message.answer(text=LEXICON_ANSWERS_RU['auth_incorrect_phone'])


@router.message(StateFilter(FSMAuthState.waiting_for_code), CorrectOTPCode())
async def auth_process_code(message: Message, state: FSMContext, code: str):
    state_data = await state.get_data()
    client = router.parent_router.workflow_data.get("tg_client")
    phone = state_data.get("phone")
    result = await auth_enter_code(client=client, phone=phone, code=code)
    match result:
        case AuthStatesEnum.CodeValid:
            db_pool = router.parent_router.workflow_data.get("db_pool")
            await end_auth(message=message, state=state, client=client, db_pool=db_pool)
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
        password: str):
    state_data = await state.get_data()
    await message.delete()
    client = router.parent_router.workflow_data.get("tg_client")
    result = await auth_enter_password(client=client, password=password)
    match result:
        case AuthStatesEnum.PasswordValid:
            db_pool = router.parent_router.workflow_data.get("db_pool")
            await end_auth(message=message, state=state, client=client, db_pool=db_pool, password=password)
            return
        case AuthStatesEnum.PasswordInvalid:
            await message.answer(text=LEXICON_ANSWERS_RU['auth_invalid_password'])


async def end_auth(
        message: Message,
        state: FSMContext,
        client: TelegramClient,
        db_pool: Pool,
        password: str = None):
    state_data = await state.get_data()
    session_path = state_data.get("session_path")
    await save_auth(db_pool=db_pool, client=client, session_path=session_path, password=password)

    button_assistant_start = KeyboardButton(
        text=LEXICON_BUTTONS_RU['assistant_start'],
        request_contact=True)
    button_person_analyze = KeyboardButton(
        text=LEXICON_BUTTONS_RU['person_analyze'],
        request_contact=True)
    keyboard_now = create_reply_kb(button_assistant_start, button_person_analyze)

    await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'], reply_markup=keyboard_now)
    await state.set_state(FSMAuthState.successful_auth)


    # по приколу смотрим чаты пользователя
    # dialogs = await client.get_dialogs()
    #
    # for dialog in dialogs:
    #     entity = dialog.entity
    #     print(f"Название чата: {dialog.name}")
    #     print(f"Тип: {type(entity)}")
    #     print(f"ID: {entity.id}")
    #     print(f"Username: {getattr(entity, 'username', None)}")
    #     print(f"Участников: {getattr(entity, 'participants_count', 'N/A')}")
    #     print("-" * 40)
