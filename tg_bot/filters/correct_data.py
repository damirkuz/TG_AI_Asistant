import logging
import re
from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message

__all__ = ["CorrectPhone", "CorrectOTPCode", "CorrectPassword"]

logger = logging.getLogger(__name__)


class CorrectPhone(BaseFilter):
    async def __call__(self, message: Message) -> Optional[dict[str, str]]:
        logger.info("Зашли в фильтр CorrectPhone для пользователя %s (%d) с сообщением: %s", message.from_user.username,
                    message.from_user.id, message.text)
        if message.contact:
            logger.debug("Фильтр CorrectPhone: получен контакт с номером %s", message.contact.phone_number)
            return {'phone': str(message.contact.phone_number)}
        phone_correct_regex = re.compile(r"^\+?7\d{10}$")
        row_message = message.text.replace(" ", "")
        if phone_correct_regex.fullmatch(row_message):
            logger.debug("Фильтр CorrectPhone: номер %s прошёл валидацию", row_message)
            return {'phone': row_message}
        logger.warning("Фильтр CorrectPhone: номер %s не прошёл валидацию", row_message)
        return None


class CorrectOTPCode(BaseFilter):
    async def __call__(self, message: Message) -> Optional[dict[str, str]]:
        logger.info("Зашли в фильтр CorrectOTPCode для пользователя %s (%d) с сообщением: %s",
                    message.from_user.username, message.from_user.id, message.text)
        if message.text.isdigit():
            logger.debug("Фильтр CorrectOTPCode: код %s прошёл валидацию", message.text)
            return {'code': str(int(message.text) - 1)}
        logger.warning("Фильтр CorrectOTPCode: код %s не прошёл валидацию", message.text)
        return False


class CorrectPassword(BaseFilter):
    async def __call__(self, message: Message) -> Optional[dict[str, str]]:
        logger.info("Зашли в фильтр CorrectPassword для пользователя %s (%d) с сообщением: %s",
                    message.from_user.username, message.from_user.id, message.text)
        if len(message.text) > 4:
            logger.debug("Фильтр CorrectPassword: пароль длиной %d прошёл валидацию", len(message.text))
            return {'password': message.text}
        logger.warning("Фильтр CorrectPassword: пароль длиной %d не прошёл валидацию", len(message.text))
        return False
