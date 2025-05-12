import asyncio

from config_data import load_config, Config
from tg_bot.main import start_tg_bot


async def main():
    config: Config = load_config()
    await start_tg_bot(config=config)


asyncio.run(main())
