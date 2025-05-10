import asyncio
import json
import logging
from datetime import datetime
from weakref import WeakValueDictionary

from redis.asyncio import Redis
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)


class RedisClientStorage:
    def __init__(self, host: str = "redis://localhost"):
        self.redis = Redis.from_url(host)
        self.local_cache = WeakValueDictionary()  # {user_id: TelegramClient}
        self.lock = asyncio.Lock()

    async def get_client(self, user_id: int, api_id: int, api_hash: str) -> TelegramClient:
        # Пытаемся получить из локального кеша
        if client := self.local_cache.get(user_id):
            if client.is_connected():
                logger.debug("Клиент Telegram для user_id=%d получен из локального кэша", user_id)
                return client
            logger.debug("Клиент Telegram для user_id=%d в кэше не подключён. Удаляем из кэша.", user_id)
            del self.local_cache[user_id]

        async with self.lock:
            # Получаем сессию из Redis
            session_data = await self.redis.get(f"tg_session:{user_id}")
            if not session_data:
                logger.warning("Сессия Telegram для user_id=%d не найдена в Redis", user_id)
                raise ValueError("Сессия не найдена")

            # Создаем клиент
            logger.debug("Создаём TelegramClient для user_id=%d из Redis", user_id)
            client = TelegramClient(
                StringSession(json.loads(session_data)['session']),
                api_id,
                api_hash
            )

            await client.connect()
            self.local_cache[user_id] = client
            logger.info("TelegramClient для user_id=%d успешно создан и подключён", user_id)
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
            logger.info("Сессия Telegram для user_id=%d успешно сохранена в Redis и локальном кэше", user_id)

    async def cleanup(self):
        """Закрыть все соединения"""
        logger.info("Выполняется очистка и отключение всех TelegramClient в RedisClientStorage")
        for client in self.local_cache.values():
            await client.disconnect()
        await self.redis.close()
        logger.info("Очистка завершена, соединения с Redis закрыты")
