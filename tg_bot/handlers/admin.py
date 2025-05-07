from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from tg_bot.filters import IsAdmin, IsNotBanned
from tg_bot.filters.is_correct_message_user import IsCorrectMessageUser
from tg_bot.keyboards import admin_menu_keyboard
from tg_bot.keyboards.inline_keyboards import get_admin_users_panel

from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU

__all__ = ['router']

from tg_bot.services import DB, BotUserDB
from tg_bot.services.database.db_functions import get_bot_statistics, get_user_detailed, ban_bot_user, \
    make_admin_bot_user

from tg_bot.states.states import FSMAdminMenu

router = Router()

router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.callback_query.filter(IsNotBanned())


@router.message(F.text == LEXICON_BUTTONS_RU['menu_admin'])
async def admin_menu_start(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['admin_menu_start'], reply_markup=admin_menu_keyboard)
    await state.set_state(FSMAdminMenu.waiting_choice)


@router.message(StateFilter(FSMAdminMenu.waiting_choice),
                F.text == LEXICON_BUTTONS_RU['admin_statistics'])
async def process_admin_menu_statistics(message: Message, db: DB):
    result = await get_bot_statistics(db)

    await message.answer(text=LEXICON_ANSWERS_RU['admin_statistics']
                         .format(
        users_count=result['registered_users'],
        accounts_count=result['connected_accounts'],
        daily_actions=result['daily_activity'],
        total_actions=result['total_activity']),
        parse_mode=ParseMode.HTML,
    )


@router.message(StateFilter(FSMAdminMenu.waiting_choice),
                F.text == LEXICON_BUTTONS_RU['admin_users'])
async def process_admin_menu_statistics(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['admin_find_user'])
    await state.set_state(FSMAdminMenu.waiting_find_user)


# если корректные данные пользователя
@router.message(StateFilter(FSMAdminMenu.waiting_find_user),
                IsCorrectMessageUser())
async def process_admin_menu_find_user(
        message: Message,
        state: FSMContext,
        bot_user: BotUserDB):
    admin_users_panel = get_admin_users_panel(
        is_banned=bot_user.is_banned,
        is_admin=bot_user.is_admin)
    await message.answer(text=LEXICON_ANSWERS_RU['admin_users_panel'], reply_markup=admin_users_panel)
    await state.update_data(bot_user=bot_user.model_dump(mode="json"))
    await state.set_state(FSMAdminMenu.waiting_choice)


# если некорректные данные пользователя
@router.message(StateFilter(FSMAdminMenu.waiting_find_user))
async def process_admin_menu_find_user(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ANSWERS_RU['admin_not_find_user'])

#
@router.callback_query(F.data == 'admin_users_panel_detailed')
async def admin_users_panel_detailed(
        callback: CallbackQuery,
        state: FSMContext,
        db: DB):
    bot_user = await get_bot_user_from_state(state)
    about_user: dict = await get_user_detailed(db, bot_user.telegram_id)
    about_bot_user = about_user.get('bot_user')
    about_tg_account = about_user.get('tg_account')
    await callback.message.answer(text=LEXICON_ANSWERS_RU['admin_detailed_user_me']
                                  .format(
        username=about_bot_user['username'],
        telegram_id=about_bot_user['telegram_id'],
        full_name=about_bot_user['full_name'],
        is_admin=about_bot_user['is_admin'],
        is_active=about_bot_user['is_active'],
        is_banned=about_bot_user['is_banned'],
        register_date=about_bot_user['created_at']),
        parse_mode=ParseMode.HTML
    )

    if about_tg_account:
        await callback.message.answer(text=LEXICON_ANSWERS_RU['admin_detailed_user_account']
                                      .format(
            telegram_id=about_tg_account['tg_user_id'],
            full_name=about_tg_account['full_name'],
            phone_number=about_tg_account['phone_number']),
            parse_mode=ParseMode.HTML
        )

# поменять статус бана
@router.callback_query(or_f(F.data == 'admin_users_panel_ban',
                       F.data == 'admin_users_panel_unban'))
async def admin_users_panel_detailed_banning(
        callback: CallbackQuery, state: FSMContext, db: DB):
    bot_user = await get_bot_user_from_state(state)
    ban_bool = callback.data == 'admin_users_panel_ban'
    await ban_bot_user(db, bot_user.telegram_id, ban_bool)
    admin_users_panel = get_admin_users_panel(
        is_banned=ban_bool, is_admin=bot_user.is_admin)
    if ban_bool:
        await callback.answer(text=LEXICON_ANSWERS_RU['admin_user_was_banned'])
    else:
        await callback.answer(text=LEXICON_ANSWERS_RU['admin_user_was_unbanned'])
    await callback.message.edit_text(text=LEXICON_ANSWERS_RU['admin_users_panel'], reply_markup=admin_users_panel)


# поменять статус администратора
@router.callback_query(or_f(F.data == 'admin_users_panel_make_admin',
                       F.data == 'admin_users_panel_unmake_admin'))
async def admin_users_panel_detailed_banning(
        callback: CallbackQuery, state: FSMContext, db: DB):
    bot_user: BotUserDB = await get_bot_user_from_state(state)
    admin_bool = callback.data == 'admin_users_panel_make_admin'
    await make_admin_bot_user(db, bot_user.telegram_id, admin_bool)
    admin_users_panel = get_admin_users_panel(
        is_banned=bot_user.is_banned, is_admin=admin_bool)
    if admin_bool:
        await callback.answer(text=LEXICON_ANSWERS_RU['admin_user_maked_admin'])
    else:
        await callback.answer(text=LEXICON_ANSWERS_RU['admin_user_unmaked_admin'])
    await callback.message.edit_text(text=LEXICON_ANSWERS_RU['admin_users_panel'], reply_markup=admin_users_panel)


async def get_bot_user_from_state(state: FSMContext) -> BotUserDB:
    state_data = await state.get_data()
    bot_user = BotUserDB(**state_data['bot_user'])
    return bot_user