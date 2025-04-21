from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.db_classes import UserDB
__all__ = ["IsRegistered"]


class IsRegistered(BaseFilter):

    async def __call__(self, message: Message, user_db: UserDB) -> bool:
        return user_db is not None and user_db.is_active

