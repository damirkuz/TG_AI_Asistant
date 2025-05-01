import asyncio
import json
from datetime import datetime

from telethon import TelegramClient
from telethon.sessions import StringSession
from weakref import WeakValueDictionary

from redis.asyncio import Redis


class RedisClientStorage:
    def __init__(self, host: str = "redis://localhost"):
        self.redis = Redis.from_url(host)
        self.local_cache = WeakValueDictionary()  # {user_id: TelegramClient}
        self.lock = asyncio.Lock()

    async def get_client(self, user_id: int, api_id: int, api_hash: str) -> TelegramClient:
        # Пытаемся получить из локального кеша
        if client := self.local_cache.get(user_id):
            if client.is_connected():
                return client
            del self.local_cache[user_id]

        async with self.lock:
            # Получаем сессию из Redis
            session_data = await self.redis.get(f"tg_session:{user_id}")
            if not session_data:
                raise ValueError("Сессия не найдена")

            # Создаем клиент
            client = TelegramClient(
                StringSession(json.loads(session_data)['session']),
                api_id,
                api_hash
            )

            await client.connect()
            self.local_cache[user_id] = client
            return client

    async def save_session(self, user_id: int, client: TelegramClient):
        async with self.lock:
            session_data = {
                "session": client.session.save(),
                "timestamp": datetime.now().isoformat()
            }
            # Сохраняем в Redis на 1 час
            await self.redis.setex(
                f"tg_session:{user_id}",
                60 * 60,
                json.dumps(session_data)
            )
            # Обновляем локальный кеш
            self.local_cache[user_id] = client

    async def cleanup(self):
        """Закрыть все соединения"""
        for client in self.local_cache.values():
            await client.disconnect()
        await self.redis.close()

