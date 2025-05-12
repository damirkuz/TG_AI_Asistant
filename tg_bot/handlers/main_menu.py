import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.keyboards.reply_keyboards import settings_menu_keyboard
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.states import FSMMainMenu, FSMSettingsState

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


@router.message(F.text == LEXICON_BUTTONS_RU['menu_find'])
async def process_start_command(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) выбрал пункт 'Найти'", message.from_user.username, message.from_user.id)
    # TODO здесь должен быть проброс на веб интерфейс
    await message.answer(text=LEXICON_ANSWERS_RU['not_done'])
    # await state.set_state(FSMMainState.find_info)


@router.message(F.text == LEXICON_BUTTONS_RU['menu_dossier'])
async def process_start_command(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) выбрал пункт 'Досье'", message.from_user.username, message.from_user.id)
    # TODO здесь должен быть проброс на веб интерфейс
    await message.answer(text=LEXICON_ANSWERS_RU['not_done'])
    # await state.set_state(FSMMainState.find_info)
