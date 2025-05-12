import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.db_functions import get_user_db

__all__ = ["IsCorrectMessageUser"]

logger = logging.getLogger(__name__)


class IsCorrectMessageUser(BaseFilter):
    async def __call__(self, message: Message) -> dict[str, int] | bool:

        logger.info("Зашли в фильтр IsCorrectMessageUser для пользователя %s (%d) с сообщением: %s",
                    message.from_user.username, message.from_user.id, message.text)

        telegram_id = None
        username = None
        if message.contact:
            telegram_id = message.contact.user_id
        elif message.text.isdigit():
            telegram_id = int(message.text)
        elif message.text.startswith('@'):
            username = message.text.lstrip('@')

        if message.contact or message.text.isdigit() or message.text.startswith('@'):
            logger.debug("Проверяем пользователя по contact/text: %s", message.text)
            bot_user = await get_user_db(user_id=telegram_id, username=username)
            if bot_user:
                logger.info("Пользователь найден в базе: %s", bot_user)
                return {"bot_user": bot_user}
            else:
                logger.warning("Пользователь не найден в базе по сообщению: %s", message.text)
        else:
            logger.warning("Сообщение не подходит под условия фильтра: %s", message.text)

        return False
