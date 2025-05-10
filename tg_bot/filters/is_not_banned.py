import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message


from tg_bot.services import get_user_db
from database import BotUserDB, DB


__all__ = ["IsNotBanned"]

logger = logging.getLogger(__name__)


class IsNotBanned(BaseFilter):
    async def __call__(self, message: Message, db: DB,
                       user_db: BotUserDB = None) -> bool:
        logger.info("Зашли в фильтр IsNotBanned")
        if user_db is None:
            user_db = await get_user_db(db=db, user_id=message.from_user.id)

        return not user_db.is_banned
