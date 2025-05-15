import asyncio
import json
import logging
from datetime import datetime
from weakref import WeakValueDictionary

from sqlalchemy import select

from database import AccountSession
from database.db_core import async_session_maker

from redis.asyncio import Redis
from telethon import TelegramClient
from telethon.sessions import StringSession

from environs import Env

__all__ = ["RedisClientStorage", "redis_client_storage", "redis"]

logger = logging.getLogger(__name__)


class RedisClientStorage:
    def __init__(self, tg_api_id: int, tg_api_hash: str, host: str = "redis://localhost"):
        self.redis = Redis.from_url(host)
        self.local_cache = WeakValueDictionary()  # {user_id: TelegramClient}
        self.lock = asyncio.Lock()
        self.tg_api_id = tg_api_id
        self.tg_api_hash = tg_api_hash

    async def get_client(self, bot_user_id: int) -> TelegramClient:
        # Пытаемся получить из локального кеша
        if client := self.local_cache.get(bot_user_id):
            if client.is_connected():
                logger.debug("Клиент Telegram для user_id=%d получен из локального кэша", bot_user_id)
                return client
            logger.debug("Клиент Telegram для user_id=%d в кэше не подключён. Удаляем из кэша.", bot_user_id)
            del self.local_cache[bot_user_id]

        async with self.lock:
            # Получаем сессию из Redis
            session_data = await self.redis.get(f"tg_session:{bot_user_id}")
            if session_data:
                tg_session_data = json.loads(session_data)['session']
            else:
                # иначе запрашиваем из базы данных
                logger.warning("Сессия Telegram для user_id=%d не найдена в Redis. Получаем из базы данных", bot_user_id)
                async with async_session_maker() as db_session:
                    account_session_line = (await db_session.execute(
                        select(AccountSession).where(AccountSession.bot_user_id == bot_user_id))).scalar_one_or_none()
                    if account_session_line:
                        tg_session_data = account_session_line.session_data
                    else:
                        raise ValueError("Сессии данного пользователя нет в базе данных")

            # Создаем клиент
            logger.debug("Создаём TelegramClient для user_id=%d из Redis", bot_user_id)
            client = TelegramClient(
                StringSession(tg_session_data),
                self.tg_api_id,
                self.tg_api_hash
            )

            await client.connect()
            self.local_cache[bot_user_id] = client
            logger.info("TelegramClient для user_id=%d успешно создан и подключён", bot_user_id)
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

    async def clear_all(self):
        await self.redis.flushdb()

env = Env()
env.read_env()

# Создаём экземпляр хранилища и redis
redis = Redis(host='localhost')
redis_client_storage = RedisClientStorage(host='redis://localhost', tg_api_id=int(env("TG_APP_API_ID")), tg_api_hash=env("TG_APP_API_HASH"))