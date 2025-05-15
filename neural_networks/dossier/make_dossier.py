import asyncio
from typing import List

from environs import Env
from faiss.contrib.datasets import username
from openai.types.responses import Response
from telethon import TelegramClient

from entity.SemanticMessage import SemanticMessage
from neural_networks.AiAPI import get_openai_client
from neural_networks.dossier.prompts import prompt_for_chunk_analyze
from redis_service import redis_client_storage
from tg_bot.services import iter_dialog_messages

env = Env()
env.read_env()

__all__ = ["DossierManager"]

class DossierManager:
    def __init__(self, api_key: str = env.str("OPENAI_API_KEY"), base_url: str = env.str("OPENAI_BASE_URL"), ai_model: str = "gpt-4.1-nano"):
        self.neuro_client = get_openai_client(api_key, base_url)
        self.ai_model = ai_model

    def make_dossier(self):
        pass



    async def chunk_analyze(self, messages: List[SemanticMessage], ai_model: str = None, username: str = None):
        if ai_model is None:
            ai_model = self.ai_model
        self.neuro_client = await get_openai_client(env.str("OPENAI_API_KEY"), env.str("OPENAI_BASE_URL"))
        messages_string = prompt_for_chunk_analyze + "Имя анализируемого человека: " + username + "\n" + "\n".join((str(x) for x in messages))
        response: Response = await self.neuro_client.responses.create(
            model=ai_model,
            input=messages_string
            # ,stream=True
            # ,timeout=600
        )
        result_text = response.output[0].content[0].text
        return result_text




    def final_analyze(self):
        pass


async def main():
    manager = DossierManager()
    semantic_messages = []
    tg_client: TelegramClient = await redis_client_storage.get_client(bot_user_id=4)
    username = (await tg_client.get_entity("@Vinogradov_dima")).username
    #
    async for message in iter_dialog_messages(client=tg_client, dialog="@Vinogradov_dima"):
        sem_message = SemanticMessage(message_id=message.id, date=message.date, date_unixtime=1234, from_user=username, from_user_id=123, text=message.message)
        semantic_messages.append(sem_message)

    print(await manager.chunk_analyze(semantic_messages, username=username))

if __name__ == "__main__":
    asyncio.run(main())
