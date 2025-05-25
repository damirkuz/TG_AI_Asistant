import logging

from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tg_bot.keyboards import create_inline_kb

__all__ = ['get_admin_users_panel', 'start_mini_app_keyboard']

from tg_bot.lexicon import LEXICON_BUTTONS_RU, LEXICON_URLS_RU

logger = logging.getLogger(__name__)


def get_admin_users_panel(is_banned: bool = False, is_admin: bool = False) -> InlineKeyboardMarkup:
    logger.info("Формируется панель администратора: is_banned=%s, is_admin=%s", is_banned, is_admin)
    buttons_name = ['admin_users_panel_detailed']

    if is_banned:
        buttons_name.append('admin_users_panel_unban')
        logger.debug("Добавлена кнопка 'unban'")
    else:
        buttons_name.append('admin_users_panel_ban')
        logger.debug("Добавлена кнопка 'ban'")

    if is_admin:
        buttons_name.append('admin_users_panel_unmake_admin')
        logger.debug("Добавлена кнопка 'unmake_admin'")
    else:
        buttons_name.append('admin_users_panel_make_admin')
        logger.debug("Добавлена кнопка 'make_admin'")

    logger.debug("Итоговый список кнопок: %s", buttons_name)
    return create_inline_kb(*buttons_name)


def get_start_mini_app_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=LEXICON_BUTTONS_RU['start_mini_app'], web_app=WebAppInfo(url=LEXICON_URLS_RU['mini_app']))
    kb.adjust(1)
    return kb.as_markup()


start_mini_app_keyboard = get_start_mini_app_keyboard()