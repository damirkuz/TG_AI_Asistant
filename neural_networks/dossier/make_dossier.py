import asyncio
from typing import List

from environs import Env
from faiss.contrib.datasets import username
from openai.types.responses import Response
from telethon import TelegramClient

from entity.SemanticMessage import SemanticMessage
from neural_networks.AiAPI.connect_to_openAI import get_openai_client
from neural_networks.dossier.prompts import prompt_for_chunk_analyze, prompt_for_final_analyze
from redis_service import redis_client_storage
from tg_bot.services import iter_dialog_messages



env = Env()
env.read_env()

__all__ = ["DossierManager"]

class DossierManager:
    def __init__(self, api_key: str = env.str("OPENAI_API_KEY"), base_url: str = env.str("OPENAI_BASE_URL"), ai_model_for_chunk: str = "gpt-4.1-nano", ai_model_for_final: str = "gpt-4.1-nano", messages_in_one_chank: int = 1000):
        self.neuro_client = get_openai_client(api_key, base_url)
        self.ai_model_for_chunk = ai_model_for_chunk
        self.ai_model_for_final = ai_model_for_final
        self.messages_in_one_chank = messages_in_one_chank

    def make_dossier(self, messages: List[SemanticMessage], username: str = None) -> str:
        if username is None:
            return "Не задан пользователь, которого надо анализировать"
        if len(messages) <= self.messages_in_one_chank:
            return self.chunk_analyze(messages, username)
        return self.final_analyze(messages, username)




    async def chunk_analyze(self, messages: List[SemanticMessage], username: str = None) -> str:
        self.neuro_client = await get_openai_client(env.str("OPENAI_API_KEY"), env.str("OPENAI_BASE_URL"))
        messages_string = prompt_for_chunk_analyze + "Имя анализируемого человека: " + username + "\n" + "\n".join((str(x) for x in messages))
        response: Response = await self.neuro_client.responses.create(
            model=self.ai_model_for_chunk,
            input=messages_string
            # ,stream=True
            # ,timeout=600
        )
        result_text = response.output[0].content[0].text
        return result_text




    async def final_analyze(self, messages: List[SemanticMessage], username: str = None, messages_in_one_chank: int = 1000) -> str:

        # Получаем отчеты разбитые по чанкам
        count_chunks = len(messages) // messages_in_one_chank;
        results = []
        for i in range(count_chunks):
            results.append(await self.chunk_analyze(messages[messages_in_one_chank * i: min(messages_in_one_chank * (i + 1), len(messages))], username))

        # Получаем отчет на основе отчетов по чанкам
        self.neuro_client = await get_openai_client(env.str("OPENAI_API_KEY"), env.str("OPENAI_BASE_URL"))
        messages_string = prompt_for_final_analyze + "Имя анализируемого человека: " + username + "\n" + "\n".join((results))
        response: Response = await self.neuro_client.responses.create(
            model=self.ai_model_for_final,
            input=messages_string
            # ,stream=True
            # ,timeout=600
        )
        result_text = response.output[0].content[0].text
        return result_text




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
