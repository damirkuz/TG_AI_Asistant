import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from telethon import TelegramClient

from config_data import Config
from database import save_auth
from database.db_functions import get_user_db
from tg_bot.filters.correct_data import CorrectPhone, CorrectOTPCode, CorrectPassword
from tg_bot.keyboards import create_reply_kb, main_menu_keyboard, main_menu_admin_keyboard
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from redis_service import RedisClientStorage
from tg_bot.services.telethon_auth import auth_send_code, AuthStatesEnum, auth_enter_code, auth_enter_password
from tg_bot.states import FSMAuthState, FSMMainMenu

__all__ = ['router', 'auth_request_phone']

router = Router()

logger = logging.getLogger(__name__)

router.message.filter(StateFilter(FSMAuthState))


@router.message(StateFilter(FSMAuthState.start_auth))
async def auth_request_phone(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) начал авторизацию (start_auth)", message.from_user.username, message.from_user.id)
    button = KeyboardButton(
        text=LEXICON_BUTTONS_RU['share_phone'],
        request_contact=True)
    keyboard_now = create_reply_kb(button)
    await message.answer(text=LEXICON_ANSWERS_RU['auth_request_phone'], reply_markup=keyboard_now)
    await state.set_state(FSMAuthState.waiting_for_phone)
    logger.debug("FSMAuthState: переведено в waiting_for_phone для пользователя %d", message.from_user.id)


@router.message(StateFilter(FSMAuthState.waiting_for_phone), CorrectPhone())
async def auth_request_code(message: Message, state: FSMContext, phone: str, config: Config,
                            redis_client_storage: RedisClientStorage):
    logger.info("Пользователь %s (%d) отправил корректный номер: %s", message.from_user.username, message.from_user.id,
                phone)
    sent_result: dict[str, TelegramClient | str] | AuthStatesEnum = await auth_send_code(config.tg_app,
                                                                                         str(message.from_user.id),
                                                                                         phone)
    if sent_result == AuthStatesEnum.PhoneNumberBanned:
        logger.warning("Попытка входа с забаненного номера: %s (user_id=%d)", phone, message.from_user.id)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_banned_phone'])
        return
    else:
        # сохраняем сессию в локальное хранилище
        tg_client = sent_result.get("tg_client")
        state_data = await state.get_data()
        bot_user_id = state_data.get('bot_user_id')
        logger.debug("Сохраняем сессию пользователя %d в Redis", bot_user_id)
        await redis_client_storage.save_session(bot_user_id, tg_client)

        await state.update_data(phone=phone)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_request_code'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMAuthState.waiting_for_code)
        logger.info("Пользователь %d: отправлен запрос на ввод кода, FSMAuthState -> waiting_for_code",
                    message.from_user.id)


@router.message(StateFilter(FSMAuthState.waiting_for_phone))
async def auth_incorrect_phone(message: Message):
    logger.warning("Пользователь %s (%d) отправил некорректный номер: %s", message.from_user.username,
                   message.from_user.id, message.text)
    await message.answer(text=LEXICON_ANSWERS_RU['auth_incorrect_phone'])


@router.message(StateFilter(FSMAuthState.waiting_for_code), CorrectOTPCode())
async def auth_process_code(message: Message, state: FSMContext, code: str,
                            redis_client_storage: RedisClientStorage, config: Config):
    logger.info("Пользователь %s (%d) ввёл код: %s", message.from_user.username, message.from_user.id, code)
    state_data = await state.get_data()
    bot_user_id = state_data.get('bot_user_id')
    client = await redis_client_storage.get_client(bot_user_id=bot_user_id)
    phone = state_data.get("phone")
    result = await auth_enter_code(client=client, phone=phone, code=code)
    logger.debug("Результат проверки кода для пользователя %d: %s", message.from_user.id, result)
    match result:
        case AuthStatesEnum.CodeValid:
            logger.info("Код подтверждён для пользователя %d", message.from_user.id)
            await end_auth(message=message, state=state, client=client)
            return
        case AuthStatesEnum.CodeInvalid:
            logger.warning("Введён неверный код для пользователя %d", message.from_user.id)
            await message.answer(text=LEXICON_ANSWERS_RU['auth_invalid_code'])
            return
        case AuthStatesEnum.CodeExpired:
            logger.warning("Введён просроченный код для пользователя %d", message.from_user.id)
            await message.answer(text=LEXICON_ANSWERS_RU['auth_expired_code'])
            await auth_request_code(message=message, state=state, phone=phone)
            return
        case AuthStatesEnum.PasswordNeeded:
            logger.info("Для пользователя %d требуется пароль", message.from_user.id)
            await message.answer(text=LEXICON_ANSWERS_RU['auth_need_password'])
            await state.set_state(FSMAuthState.waiting_for_password)
            logger.debug("FSMAuthState: переведено в waiting_for_password для пользователя %d", message.from_user.id)


@router.message(StateFilter(FSMAuthState.waiting_for_code))
async def auth_process_incorrect_code(message: Message):
    logger.warning("Пользователь %s (%d) ввёл некорректный код: %s", message.from_user.username, message.from_user.id,
                   message.text)
    await message.answer(text=LEXICON_ANSWERS_RU['auth_message_incorrect_code'])


@router.message(StateFilter(FSMAuthState.waiting_for_password),
                CorrectPassword())
async def auth_process_code(
        message: Message,
        state: FSMContext,
        password: str,
        redis_client_storage: RedisClientStorage,
        config: Config):
    logger.info("Пользователь %s (%d) вводит пароль", message.from_user.username, message.from_user.id)
    state_data = await state.get_data()
    await message.delete()
    bot_user_id = state_data.get('bot_user_id')
    client = await redis_client_storage.get_client(bot_user_id=bot_user_id)

    result = await auth_enter_password(client=client, password=password)
    logger.debug("Результат проверки пароля для пользователя %d: %s", message.from_user.id, result)
    match result:
        case AuthStatesEnum.PasswordValid:
            logger.info("Пароль подтверждён для пользователя %d", message.from_user.id)
            await end_auth(message=message, state=state, client=client, password=password)
            return
        case AuthStatesEnum.PasswordInvalid:
            logger.warning("Введён неверный пароль для пользователя %d", message.from_user.id)
            await message.answer(text=LEXICON_ANSWERS_RU['auth_invalid_password'])


async def end_auth(
        message: Message,
        state: FSMContext,
        client: TelegramClient,
        password: str = None):
    logger.info("Авторизация завершена для пользователя %s (%d)", message.from_user.username, message.from_user.id)
    state_data = await state.get_data()
    await save_auth(client=client, password=password,
                    bot_user_id=state_data.get('bot_user_id'))
    logger.debug("Сессия пользователя %d сохранена в базе", message.from_user.id)
    user_db = await get_user_db(user_id=message.from_user.id)
    if user_db.is_admin:
        logger.info("Пользователь %s (%d) - админ, отправлена админ-меню", message.from_user.username,
                    message.from_user.id)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'], reply_markup=main_menu_admin_keyboard)
    else:
        logger.info("Пользователь %s (%d) - не админ, отправлено обычное меню", message.from_user.username,
                    message.from_user.id)
        await message.answer(text=LEXICON_ANSWERS_RU['auth_successful'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)
    logger.debug("FSMMainMenu: переведено в waiting_choice для пользователя %d", message.from_user.id)
