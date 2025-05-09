from aiogram.filters import BaseFilter
from aiogram.types import Message
__all__ = ["IsNotBanned"]

from tg_bot.services import get_user_db
from tg_bot.services.database import BotUserDB


class IsNotBanned(BaseFilter):
    async def __call__(self, message: Message, user_db: BotUserDB = None) -> bool:
        if user_db is None:
            user_db = await get_user_db(message.from_user.id)

        return not user_db.is_banned
