import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import BotUserDB
from tg_bot.filters.haveConnnectedAccount import HaveConnectedAccount
from tg_bot.keyboards.reply_keyboards import settings_menu_keyboard
from tg_bot.keyboards.inline_keyboards import start_mini_app_keyboard

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.states import FSMMainMenu, FSMSettingsState

from tg_bot.services.telethon_fetch import update_user_db_chats


__all__ = ['router']

router = Router()

logger = logging.getLogger(__name__)

router.message.filter(StateFilter(FSMMainMenu))


@router.message(F.text == LEXICON_BUTTONS_RU['menu_settings'])
async def process_start_command(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) открыл меню настроек", message.from_user.username, message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_menu'], reply_markup=settings_menu_keyboard)
    await state.set_state(FSMSettingsState.waiting_choice)
    logger.debug("FSMSettingsState: переведено в waiting_choice для пользователя %d", message.from_user.id)


@router.message(F.text == LEXICON_BUTTONS_RU['menu_find'], HaveConnectedAccount())
async def process_menu_find(message: Message, state: FSMContext, user_db: BotUserDB):
    logger.info("Пользователь %s (%d) выбрал пункт 'Найти'", message.from_user.username, message.from_user.id)
    # TODO здесь должен быть проброс на веб интерфейс
    await update_user_db_chats(user_db.id)
    await message.answer(text=LEXICON_ANSWERS_RU['start_mini_app_find'], reply_markup=start_mini_app_keyboard)
    # await state.set_state(FSMMainState.find_info)


# сюда попадёт пользователь без привязанного аккаунта
@router.message(F.text == LEXICON_BUTTONS_RU['menu_find'])
async def process_menu_find(message: Message):
    logger.info("Пользователь %s (%d) выбрал пункт 'Найти', НО не привязал аккаунт", message.from_user.username, message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['not_connected_account'])


@router.message(F.text == LEXICON_BUTTONS_RU['menu_dossier'], HaveConnectedAccount())
async def process_menu_dossier(message: Message, state: FSMContext, user_db: BotUserDB):
    logger.info("Пользователь %s (%d) выбрал пункт 'Досье'", message.from_user.username, message.from_user.id)
    # TODO здесь должен быть проброс на веб интерфейс
    await update_user_db_chats(user_db.id)
    await message.answer(text=LEXICON_ANSWERS_RU['start_mini_app_dossier'], reply_markup=start_mini_app_keyboard)
    # await state.set_state(FSMMainState.find_info)


# сюда попадёт пользователь без привязанного аккаунта
@router.message(F.text == LEXICON_BUTTONS_RU['menu_dossier'])
async def process_menu_find(message: Message):
    logger.info("Пользователь %s (%d) выбрал пункт 'Досье', НО не привязал аккаунт", message.from_user.username, message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['not_connected_account'])