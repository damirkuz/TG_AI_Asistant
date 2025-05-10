import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

__all__ = ["IsAdmin"]

from database.db_functions import get_user_db
from database import BotUserDB

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message,
                       user_db: BotUserDB = None) -> bool:
        logger.info("Зашли в фильтр IsAdmin для пользователя %s (%d)", message.from_user.username, message.from_user.id)
        if user_db is None:
            logger.debug("user_db не передан, получаем из базы для пользователя %d", message.from_user.id)
            user_db = await get_user_db(user_id=message.from_user.id)

        logger.debug("user_db.is_admin для пользователя %d: %s", message.from_user.id, user_db.is_admin)
        return user_db.is_admin
