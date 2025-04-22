from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import StateFilter
from tg_bot.keyboards.reply_keyboards import settings_menu_keyboard
from tg_bot.states import FSMMainState

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']


router = Router()

router.message.filter(StateFilter(FSMMainState))


@router.message(StateFilter(FSMMainState.main_menu),
                F.text == LEXICON_BUTTONS_RU['menu_settings'])
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['settings_menu'], reply_markup=settings_menu_keyboard)
    await state.set_state(FSMMainState.settings_menu)


@router.message(StateFilter(FSMMainState.main_menu),
                F.text == LEXICON_BUTTONS_RU['menu_find'])
async def process_start_command(message: Message, state: FSMContext):
    # TODO здесь должен быть проброс на веб интерфейс
    await message.answer(text=LEXICON_ANSWERS_RU['not_done'])
    # await state.set_state(FSMMainState.find_info)


@router.message(StateFilter(FSMMainState.main_menu),
                F.text == LEXICON_BUTTONS_RU['menu_dossier'])
async def process_start_command(message: Message, state: FSMContext):
    # TODO здесь должен быть проброс на веб интерфейс
    await message.answer(text=LEXICON_ANSWERS_RU['not_done'])
    # await state.set_state(FSMMainState.find_info)


@router.message(StateFilter(FSMMainState.main_menu),
                F.text == LEXICON_BUTTONS_RU['menu_admin'])
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['not_done'])
    # await state.set_state(FSMMainState.find_info)
