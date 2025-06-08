import asyncio

from telethon import TelegramClient

from redis_service import redis_client_storage
from tg_bot.services.telethon_fetch import iter_dialog_messages

async def main():
    tg_client: TelegramClient = await redis_client_storage.get_client(bot_user_id=2)
    async for message in iter_dialog_messages(client=tg_client, dialog="@be_2nd"):
        print(message)
        input()


if __name__ == '__main__':
    asyncio.run(main())