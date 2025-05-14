import asyncio
import logging
from datetime import datetime
from typing import AsyncGenerator, Union

import pytz
from telethon.errors import FloodWaitError
from telethon.sync import TelegramClient
from telethon.tl.types import Message, Dialog, Chat

__all__ = ["iter_dialog_messages"]

from redis_service import redis_client_storage

logger = logging.getLogger(__name__)


async def iter_dialog_messages(client: TelegramClient, dialog: Union[Dialog, str, int], start_date: datetime = None,
                               end_date: datetime = None) -> AsyncGenerator[Message, None]:
    '''
    Возвращает итератор сообщений по заданным параметрам

    result = iter_dialog_messages(client, need_dialog, start_date=datetime(year=2024, month=4, day=1), end_date=datetime(year=2024, month=5, day=1))

    async for m in result:
        print(m.message[:10])
    '''

    logger.info("Начало итерации сообщений: dialog=%s, start_date=%s, end_date=%s", str(dialog), str(start_date),
                str(end_date))
    dialog = await client.get_entity(dialog)

    # Устанавливаем часовой пояс
    tz = pytz.timezone('Europe/Moscow')
    if start_date and start_date.tzinfo is None:
        start_date = tz.localize(start_date)
    if end_date and end_date and end_date.tzinfo is None:
        end_date = tz.localize(end_date)

    current_offset_date = start_date

    while True:
        try:
            async for message in client.iter_messages(dialog, reverse=True, offset_date=current_offset_date):
                msg_date = message.date.astimezone(tz)

                if end_date and msg_date > end_date:
                    logger.debug("Достигнут конец диапазона дат: %s > %s", msg_date, end_date)
                    break

                yield message
                current_offset_date = msg_date  # запоминаем, где остановились
                await asyncio.sleep(0.05)
            logger.info("Итерация сообщений завершена для dialog=%s", str(dialog))
            break  # завершили нормально
        except FloodWaitError as e:
            logger.warning("Flood wait: ждём %d секунд при получении сообщений из dialog=%s", e.seconds, str(dialog))
            await asyncio.sleep(e.seconds + 1)
            # после паузы продолжим с current_offset_date


async def get_chats(client: TelegramClient):
    result = await client.get_me()
    print(result)
    # print(await client.get_dialogs())
    # async for i in client.iter_dialogs():
    #     print(i)
    #     input()

async def main():
    tg_client: TelegramClient = await redis_client_storage.get_client(bot_user_id=3)
    # await get_chats(tg_client)


if __name__ == '__main__':
    asyncio.run(main())