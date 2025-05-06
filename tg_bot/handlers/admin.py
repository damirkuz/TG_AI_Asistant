from typing import Dict, Any

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.filters import IsAdmin
from tg_bot.keyboards import admin_menu_keyboard

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']

from tg_bot.services import DB

from tg_bot.states.states import FSMAdminMenu

router = Router()

router.filter = IsAdmin()


@router.message(F.text == LEXICON_BUTTONS_RU['menu_admin'])
async def admin_menu_start(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['admin_menu_start'], reply_markup=admin_menu_keyboard)
    await state.set_state(FSMAdminMenu.waiting_choice)


@router.message(StateFilter(FSMAdminMenu.waiting_choice),
                F.text == LEXICON_BUTTONS_RU['admin_statistics'])
async def process_admin_menu_statistics(message: Message, db: DB):
    result = await db.fetch_one("""SELECT
            (SELECT COUNT(*) FROM bot_users) AS registered_users,
            (SELECT COUNT(*) FROM tg_accounts) AS connected_accounts,
            (SELECT COUNT(*) FROM statistics) AS total_activity,
            (SELECT COUNT(*) FROM statistics WHERE created_at >= NOW() - INTERVAL '1 day') AS daily_activity;
    """)

    await message.answer(text=LEXICON_ANSWERS_RU['admin_statistics']
                                .format(
                                users_count=result['registered_users'],
                                accounts_count=result['connected_accounts'],
                                daily_actions=result['daily_activity'],
                                total_actions=result['total_activity'],),
                        parse_mode=ParseMode.HTML,
    )


@router.message(StateFilter(FSMAdminMenu.waiting_choice),
                F.text == LEXICON_BUTTONS_RU['admin_users'])
async def process_admin_menu_statistics(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['not_done'], reply_markup=admin_menu_keyboard)
