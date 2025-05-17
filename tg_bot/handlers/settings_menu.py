import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from telethon import TelegramClient

from database import save_auth, delete_user_in_db
from database.db_functions import get_user_db
from tg_bot.filters import IsCorrectSession
from tg_bot.handlers.auth import auth_request_phone
from tg_bot.keyboards.reply_keyboards import settings_add_telegram_keyboard, main_menu_keyboard, \
    main_menu_admin_keyboard
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.states import FSMSettingsState, FSMMainMenu, FSMAuthState

__all__ = ['router']

router = Router()

logger = logging.getLogger(__name__)

router.message.filter(StateFilter(FSMSettingsState))


@router.message(StateFilter(FSMSettingsState.waiting_choice), F.text == LEXICON_BUTTONS_RU['settings_add_telegram'])
async def add_telegram(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) выбрал добавление Telegram-аккаунта через меню", message.from_user.username,
                message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_menu'],
                         reply_markup=settings_add_telegram_keyboard)


# авторизация по сессии
@router.message(F.text == LEXICON_BUTTONS_RU['settings_add_telegram_session'])
async def add_telegram_session(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) выбрал авторизацию по сессии", message.from_user.username, message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_session'])
    await state.set_state(FSMSettingsState.waiting_session_file)
    logger.debug("FSMSettingsState: переведено в waiting_session_file для пользователя %d", message.from_user.id)


@router.message(StateFilter(FSMSettingsState.waiting_session_file), IsCorrectSession())
async def waiting_session_file(message: Message, state: FSMContext, client: TelegramClient):
    logger.info("Пользователь %s (%d) загрузил корректный session-файл", message.from_user.username,
                message.from_user.id)
    state_data = await state.get_data()
    await save_auth(client=client, bot_user_id=state_data.get('bot_user_id'))
    logger.debug("Сессия пользователя %d сохранена в базе", message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_session_good'])
    user_db = await get_user_db(user_id=message.from_user.id)
    if user_db.is_admin:
        logger.info("Пользователь %s (%d) - админ, возвращается в админ-меню", message.from_user.username,
                    message.from_user.id)
        await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_admin_keyboard)
    else:
        logger.info("Пользователь %s (%d) - не админ, возвращается в обычное меню", message.from_user.username,
                    message.from_user.id)
        await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)
    logger.debug("FSMMainMenu: переведено в waiting_choice для пользователя %d", message.from_user.id)


# сюда попадёт если неправильный session файл
@router.message(StateFilter(FSMSettingsState.waiting_session_file))
async def waiting_session_file(message: Message, state: FSMContext):
    logger.warning("Пользователь %s (%d) загрузил некорректный session-файл", message.from_user.username,
                   message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_session_bad'])


# авторизация по телефону
@router.message(F.text == LEXICON_BUTTONS_RU['settings_add_telegram_phone'])
async def add_telegram_session(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) выбрал авторизацию по телефону", message.from_user.username, message.from_user.id)
    await state.set_state(FSMAuthState.start_auth)
    logger.debug("FSMAuthState: переведено в start_auth для пользователя %d", message.from_user.id)
    await auth_request_phone(message=message, state=state)


@router.message(StateFilter(FSMSettingsState.waiting_choice), F.text == LEXICON_BUTTONS_RU['settings_delete_my_data'])
async def settings_delete_my_data(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) запросил удаление своих данных", message.from_user.username, message.from_user.id)
    await delete_user_in_db(telegram_id=message.from_user.id)
    logger.debug("Данные пользователя %d удалены из базы", message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_delete_my_data'])
