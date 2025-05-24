import logging

from tg_bot.keyboards import create_reply_kb

__all__ = ['main_menu_keyboard', 'main_menu_admin_keyboard', 'settings_menu_keyboard', 'settings_add_telegram_keyboard',
           'admin_menu_keyboard']

logger = logging.getLogger(__name__)

main_menu_keyboard = create_reply_kb(
    'menu_settings',
    'menu_find',
    'menu_dossier',
    width=2)

main_menu_admin_keyboard = create_reply_kb(
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

admin_menu_keyboard = create_reply_kb(
    'admin_statistics',
    'admin_users',
    'back_to_main_menu',
    width=2
)

logger.info("Клавиатуры меню успешно созданы")