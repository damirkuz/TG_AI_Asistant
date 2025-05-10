from aiogram.filters import BaseFilter
from aiogram.types import Message

__all__ = ["IsCorrectMessageUser"]

from database import DB
from database import get_user_tg_id_in_db


class IsCorrectMessageUser(BaseFilter):
    async def __call__(self, message: Message, db: DB) -> dict[str, int] | bool:
        if message.contact or message.text.isdigit() or message.text.startswith('@'):
            bot_user = await get_user_tg_id_in_db(db, message)
            if bot_user:
                return {"bot_user": bot_user}

        return False
