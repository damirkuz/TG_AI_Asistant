from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from typing import Callable, Dict, Any, Awaitable


from tg_bot.lexicon import LEXICON_BUTTONS_RU
from tg_bot.services import get_user_db

__all__ = ["LoadUserDbMiddleware"]

class LoadUserDbMiddleware(BaseMiddleware):

    def __init__(self):
        self.need_messages = {"/start", LEXICON_BUTTONS_RU['menu_admin'], LEXICON_BUTTONS_RU['admin_statistics'],
                              LEXICON_BUTTONS_RU['admin_users']}

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Проверяем, что это сообщение и есть from_user
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        # Проверяем команду /start
        if isinstance(event, Message) and event.text and event.text.strip() in self.need_messages:
            try:
                # Проверяем, не загружен ли user_db ранее
                if "user_db" not in data:
                    user_db = await get_user_db(event.from_user.id)
                    data["user_db"] = user_db
            except Exception as e:
                print(f"Ошибка БД: {e}")

        return await handler(event, data)
