import asyncio

from config_data import load_config, Config
from tg_bot.main import start_tg_bot
from async_logging import setup_async_logging


async def main():
    # настраиваем асинхронное логгирование
    setup_async_logging()
    # загружаем конфиг
    config: Config = load_config()
    # запускаем тг бота
    await start_tg_bot(config=config)


asyncio.run(main())
