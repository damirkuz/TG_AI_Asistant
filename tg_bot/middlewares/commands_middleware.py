from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, User
from typing import Callable, Dict, Any, Awaitable

from asyncpg import Pool

from database.db_classes import UserDB

__all__ = ["CommandsMiddleware"]

class CommandsMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Проверяем: это команда /start
        if event.text and event.text.startswith("/start"):
            user_id = event.from_user.id
            db_pool: Pool = data['db_pool']
            async with db_pool.acquire() as conn:
                user_record = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", user_id)
                user_db = UserDB(**dict(user_record)) if user_record else None

            data["user_db"] = user_db  # Передаём в хендлер
        return await handler(event, data)
