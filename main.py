import asyncio
import random
from config_data import load_config, Config
from tg_bot.main import start_tg_bot


async def main():
    config: Config = load_config()
    await start_tg_bot(config=config)


    # about = await client.get_me()
    # print(about)
    # chat_id = 5242029465
    # dialogs = await client.get_dialogs()
    # messages = await fetch_messages(client, chat_id=chat_id)


asyncio.run(main())
