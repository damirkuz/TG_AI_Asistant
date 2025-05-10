import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message
__all__ = ["IsAdmin"]

from tg_bot.services import get_user_db
from database import DB
from database import BotUserDB


logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, db: DB,
                       user_db: BotUserDB = None) -> bool:
        logger.info("Зашли в фильтр IsAdmin")
        if user_db is None:
            user_db = await get_user_db(db=db, user_id=message.from_user.id)

        return user_db.is_admin
