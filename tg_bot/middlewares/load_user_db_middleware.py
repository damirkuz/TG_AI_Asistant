import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from tg_bot.lexicon import LEXICON_BUTTONS_RU
from tg_bot.services import get_user_db

__all__ = ["LoadUserDbMiddleware"]

logger = logging.getLogger(__name__)


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
                    db = data.get("db")
                    logger.debug("Загрузка user_db для пользователя %s (%d) по сообщению: %s", event.from_user.username,
                                 event.from_user.id, event.text)
                    user_db = await get_user_db(db=db, user_id=event.from_user.id)
                    data["user_db"] = user_db
                    logger.info("user_db успешно загружен для пользователя %s (%d)", event.from_user.username,
                                event.from_user.id)
            except Exception as e:
                logger.error(f"Ошибка БД при загрузке user_db для пользователя %s (%d): %s", event.from_user.username,
                             event.from_user.id, e)

        return await handler(event, data)
