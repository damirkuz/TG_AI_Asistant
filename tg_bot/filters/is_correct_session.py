import asyncio
import os
import random
import logging
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
        logger.info("Зашли в фильтр IsCorrectSession")
        document: Document = message.document

        if not document:
            return False

        file_name = document.file_name
        file_id = document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_size = file.file_size


        if not file_name.endswith(".session"):
            return False

        max_size = 1 * 1024 * 1024  # 1 мегабайт
        if file_size > max_size:
            return False


        # Скачивание файла
        file_data = await bot.download_file(file_path)

        # формируем путь для временного сохранения файла
        file_setted_path = f"sessions/{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_{random.randint(1000, 9999)}_{document.file_name}"

        return await IsCorrectSession.check_session_file(file_setted_path, file_data, config)

    @staticmethod
    async def check_session_file(file_path: str, file_data: BinaryIO, config: Config) -> bool | dict[str, TelegramClient]:
        with open(file_path, "wb") as f:
            f.write(file_data.read())

        try:
            try_сlient = TelegramClient(file_path, config.tg_app.api_id, config.tg_app.api_hash)
            await try_сlient.connect()
        except Exception as e: # почему-то некорректная сессия проходит как DatabaseError
            return False
        finally:
            # удаляем файл
            try:
                await asyncio.to_thread(os.remove, file_path)
            except FileNotFoundError:
                pass

        if try_сlient.is_connected():
            session_string = StringSession.save(try_сlient.session)
            return {'client': try_сlient, 'session_string': session_string}
        else:
            return False


