import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import BotUserDB
from database.db_functions import get_user_db

__all__ = ["IsRegistered"]

logger = logging.getLogger(__name__)


class IsRegistered(BaseFilter):
    async def __call__(self, message: Message,
                       user_db: BotUserDB = None) -> bool:
        logger.info("Зашли в фильтр IsRegistered для пользователя %s (%d)", message.from_user.username,
                    message.from_user.id)
        if user_db is None:
            logger.debug("user_db не передан, получаем из базы для пользователя %d", message.from_user.id)
            user_db = await get_user_db(user_id=message.from_user.id)
        logger.debug("user_db для пользователя %d: %s, is_active: %s", message.from_user.id, user_db,
                     getattr(user_db, 'is_active', None))
        return user_db is not None and user_db.is_active
