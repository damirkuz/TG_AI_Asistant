import asyncio
import logging
import os
import random
from datetime import datetime
from typing import BinaryIO

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message, Document
from telethon import TelegramClient
from telethon.sessions import StringSession

from config_data import Config

logger = logging.getLogger(__name__)

__all__ = ["IsCorrectSession"]


class IsCorrectSession(BaseFilter):

    async def __call__(self, message: Message, bot: Bot, config: Config) -> bool | dict[str, TelegramClient]:
        logger.info("Зашли в фильтр IsCorrectSession для пользователя %s (%d)", message.from_user.username,
                    message.from_user.id)
        document: Document = message.document

        if not document:
            logger.warning("Фильтр IsCorrectSession: документ не найден в сообщении пользователя %s (%d)",
                           message.from_user.username, message.from_user.id)
            return False

        file_name = document.file_name
        file_id = document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_size = file.file_size

        logger.debug("Фильтр IsCorrectSession: получен файл %s (размер %d байт) от пользователя %s (%d)", file_name,
                     file_size, message.from_user.username, message.from_user.id)

        if not file_name.endswith(".session"):
            logger.warning("Фильтр IsCorrectSession: файл %s не имеет расширения .session", file_name)
            return False

        max_size = 1 * 1024 * 1024  # 1 мегабайт
        if file_size > max_size:
            logger.warning("Фильтр IsCorrectSession: файл %s превышает максимальный размер (%d > %d)", file_name,
                           file_size, max_size)
            return False

        # Скачивание файла
        logger.debug("Фильтр IsCorrectSession: скачиваем файл %s", file_name)
        file_data = await bot.download_file(file_path)

        # формируем путь для временного сохранения файла
        file_setted_path = f"sessions/{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_{random.randint(1000, 9999)}_{document.file_name}"
        logger.debug("Фильтр IsCorrectSession: временный путь для файла - %s", file_setted_path)

        return await IsCorrectSession.check_session_file(file_setted_path, file_data, config)

    @staticmethod
    async def check_session_file(file_path: str, file_data: BinaryIO, config: Config) -> bool | dict[
        str, TelegramClient]:
        logger = logging.getLogger(__name__)
        logger.debug("Проверка session-файла по пути %s", file_path)
        with open(file_path, "wb") as f:
            f.write(file_data.read())

        try:
            try_сlient = TelegramClient(file_path, config.tg_app.api_id, config.tg_app.api_hash)
            await try_сlient.connect()
        except Exception as e:  # почему-то некорректная сессия проходит как DatabaseError
            logger.error("Ошибка при подключении через session-файл %s: %s", file_path, str(e))
            return False
        finally:
            # удаляем файл
            try:
                await asyncio.to_thread(os.remove, file_path)
                logger.debug("Временный session-файл %s удалён", file_path)
            except FileNotFoundError:
                logger.warning("Временный session-файл %s не найден для удаления", file_path)

        if try_сlient.is_connected() and await try_сlient.is_user_authorized():
            logger.info("Session-файл %s успешно проверен и подключён", file_path)
            return {'client': try_сlient}
        else:
            logger.warning("Session-файл %s не прошёл проверку: клиент не подключён", file_path)
            return False
