from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from tg_bot.keyboards import create_reply_kb

__all__ = ['main_menu_keyboard', 'settings_menu_keyboard', 'settings_add_telegram_keyboard']


main_menu_keyboard = create_reply_kb(
    'menu_settings',
    'menu_find',
    'menu_dossier',
    'menu_admin', width=2)

settings_menu_keyboard = create_reply_kb(
    'settings_add_telegram',
    'settings_AI_API_key',
    'settings_LLM_model',
    'settings_history_actions',
    'settings_my_statistics',
    'settings_delete_my_data',
    'back_to_main_menu',
    width=3)

settings_add_telegram_keyboard = create_reply_kb(
    'settings_add_telegram_session',
    'settings_add_telegram_phone',
    'back_to_main_menu'
)