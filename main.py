import asyncio
import random
from telegram_actions import login_tg, fetch_messages

async def main():
    client = await login_tg(f"id_example{random.randint(0,1000)}")
    about = await client.get_me()
    print(about)
    # chat_id = 5242029465
    # dialogs = await client.get_dialogs()
    # messages = await fetch_messages(client, chat_id=chat_id)

asyncio.run(main())