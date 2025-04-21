from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from tg_bot.keyboards import create_reply_kb

__all__ = ['main_menu_keyboard']



main_menu_keyboard = create_reply_kb('menu_settings', 'menu_find', 'menu_dossier', 'menu_admin')