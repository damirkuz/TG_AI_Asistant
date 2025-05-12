from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Dict, Any, Callable, Awaitable
import time

from tg_bot.lexicon import LEXICON_ANSWERS_RU
from tg_bot.services import DB


class BanCheckMiddleware(BaseMiddleware):
    banned_users_cache = {} # telegram_id: (is_banned, timestamp)
    cache_expire_time = 300 # кэш действителен 5 минут

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        # Проверяем кэш
        if user_id in type(self).banned_users_cache:
            is_banned, timestamp = type(self).banned_users_cache[user_id]
            # Если кэш актуален
            if current_time - timestamp < type(self).cache_expire_time:
                if is_banned:
                    return await event.answer(LEXICON_ANSWERS_RU['you_banned'])
                return await handler(event, data)

        # Запрос к БД только если нет в кэше или кэш устарел
        db = DB.get_db()
        is_banned = await db.fetch_val("SELECT is_banned FROM bot_users WHERE telegram_id = $1", user_id)

        if is_banned:
            # Пользователь забанен
            type(self).banned_users_cache[user_id] = (True, current_time)
            return await event.answer(LEXICON_ANSWERS_RU['you_banned'])

        # Пользователь не забанен или не найден
        type(self).banned_users_cache[user_id] = (False, current_time)
        return await handler(event, data)

    @classmethod
    def clear_user_cache(cls, telegram_id: str):
        cls.banned_users_cache.pop(telegram_id, None)