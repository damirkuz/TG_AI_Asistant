import asyncio
from datetime import datetime
from typing import AsyncGenerator, Union

import pytz
from telethon.errors import FloodWaitError
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message, Dialog




async def iter_dialog_messages(client: TelegramClient, dialog: Union[Dialog, str, int], start_date: datetime = None, end_date: datetime = None) -> AsyncGenerator[Message, None]:
    '''
    Возвращает итератор сообщений по заданным параметрам

    result = iter_dialog_messages(client, need_dialog, start_date=datetime(year=2024, month=4, day=1), end_date=datetime(year=2024, month=5, day=1))

    async for m in result:
        print(m.message[:10])
    '''

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
                    break

                yield message
                current_offset_date = msg_date  # запоминаем, где остановились
                await asyncio.sleep(0.05)
            break  # завершили нормально
        except FloodWaitError as e:
            print(f"Flood wait ждём {e.seconds} секунд")
            await asyncio.sleep(e.seconds + 1)
            # после паузы продолжим с current_offset_date



# API_ID =
# API_HASH = ''
# SESSION_STRING = ''

# # Пример использования функции iter_dialog_messages
# async def main():
#     client: TelegramClient = TelegramClient(session=StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH)
#     await client.connect()
#
#
#     # result = iter_dialog_messages(client, need_dialog, start_date=datetime(year=2024, month=4, day=1), end_date=datetime(year=2024, month=5, day=1))
#     result = iter_dialog_messages(client, -1001717502395)
#     async for m in result:
#         if m.message is not None:
#             print(m.message)
#
# if __name__ == '__main__':
#     asyncio.run(main())