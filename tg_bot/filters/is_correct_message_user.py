import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import DB
from database import get_user_tg_id_in_db

__all__ = ["IsCorrectMessageUser"]

logger = logging.getLogger(__name__)


class IsCorrectMessageUser(BaseFilter):
    async def __call__(self, message: Message, db: DB) -> dict[str, int] | bool:

        logger.info("Зашли в фильтр IsCorrectMessageUser для пользователя %s (%d) с сообщением: %s",
                    message.from_user.username, message.from_user.id, message.text)
        if message.contact or message.text.isdigit() or message.text.startswith('@'):
            logger.debug("Проверяем пользователя по contact/text: %s", message.text)
            bot_user = await get_user_tg_id_in_db(db, message)
            if bot_user:
                logger.info("Пользователь найден в базе: %s", bot_user)
                return {"bot_user": bot_user}
            else:
                logger.warning("Пользователь не найден в базе по сообщению: %s", message.text)
        else:
            logger.warning("Сообщение не подходит под условия фильтра: %s", message.text)

        return False
