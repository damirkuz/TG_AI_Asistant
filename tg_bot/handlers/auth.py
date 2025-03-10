
from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, KeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient

from tg_bot.filters.correct_data import CorrectPhone, CorrectOTPCode, CorrectPassword
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.states import FSMAuthState
from tg_bot.keyboards import create_reply_kb

from telegram_actions import auth_send_code, AuthStatesEnum, auth_enter_code, auth_enter_password, save_auth

__all__ = ['router']



router = Router()


@router.message(StateFilter(default_state), F.text == LEXICON_BUTTONS_RU['register'])
async def auth_request_phone(message: Message, state: FSMContext):
    button = KeyboardButton(text=LEXICON_BUTTONS_RU['share_phone'], request_contact=True)
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
        await state.update_data(sent_result)
        await state.update_data(phone=phone)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_request_code'])
        await state.set_state(FSMAuthState.waiting_for_code)


@router.message(StateFilter(FSMAuthState.waiting_for_phone))
async def auth_incorrect_phone(message: Message):
    await message.answer(text=LEXICON_ANSWERS_RU['auth_incorrect_phone'])


@router.message(StateFilter(FSMAuthState.waiting_for_code), CorrectOTPCode())
async def auth_process_code(message: Message, state: FSMContext, code: str):
    state_data = await state.get_data()
    client = state_data.get("tg_client")
    phone = state_data.get("phone")
    result = await auth_enter_code(client=client, phone=phone, code=code)
    print(result)
    match result:
        case AuthStatesEnum.CodeValid:
            await save_auth(client=client, session_path=state_data.get("session_path"), phone=state_data.get("phone"))
            await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'])
            await state.set_state(FSMAuthState.successful_auth)
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


@router.message(StateFilter(FSMAuthState.waiting_for_password), CorrectPassword())
async def auth_process_code(message: Message, state: FSMContext, password: str):
    state_data = await state.get_data()
    await message.delete()
    client = state_data.get("tg_client")
    result = await auth_enter_password(client=client, password=password)
    match result:
        case AuthStatesEnum.PasswordValid:
            await save_auth(client=client, session_path=state_data.get("session_path"), phone=state_data.get("phone"), password=password)
            await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'])
            await state.set_state(FSMAuthState.successful_auth)
            return
        case AuthStatesEnum.PasswordInvalid:
            await message.answer(text=LEXICON_ANSWERS_RU['auth_invalid_password'])