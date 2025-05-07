from aiogram.types import InlineKeyboardMarkup

from tg_bot.keyboards import create_inline_kb

__all__ = ['get_admin_users_panel']



def get_admin_users_panel(is_banned: bool = False, is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons_name = ['admin_users_panel_detailed']

    if is_banned:
        buttons_name.append('admin_users_panel_unban')
    else:
        buttons_name.append('admin_users_panel_ban')

    if is_admin:
        buttons_name.append('admin_users_panel_unmake_admin')
    else:
        buttons_name.append('admin_users_panel_make_admin')

    return create_inline_kb(*buttons_name)