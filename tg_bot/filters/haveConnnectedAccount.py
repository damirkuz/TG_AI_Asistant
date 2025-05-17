import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

__all__ = ["HaveConnectedAccount"]

from database.db_functions import check_have_connected_account
from database import BotUserDB

logger = logging.getLogger(__name__)


class HaveConnectedAccount(BaseFilter):
    async def __call__(self, message: Message, user_db: BotUserDB) -> bool:
        logger.info("Зашли в фильтр HaveConnectedAccount для пользователя %s (%d)", message.from_user.username, message.from_user.id)

        result = await check_have_connected_account(user_db.id)
        if result:
            logger.info("Нашли привязанный аккаунт для пользователя %s (%d)", message.from_user.username, message.from_user.id)
            return True
        logger.info("НЕ нашли привязанный аккаунт для пользователя %s (%d)", message.from_user.username,
                    message.from_user.id)
        return False

