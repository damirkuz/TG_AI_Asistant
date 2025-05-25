import logging
from typing import Optional

from openai import AsyncOpenAI, APIError

__all__ = ['get_openai_client']

logger = logging.getLogger(__name__)


async def get_openai_client(api_key: str, base_url: str, *args, **kwargs) -> Optional[AsyncOpenAI]:
    # cоздаём клиент
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, *args, **kwargs)

    # проверяем api_key
    try:
        result = await client.models.list()
    except APIError:
        logger.exception("Не удалось подключиться к серверу OpenAI с ключом: %s", api_key)
        return None
    if result:
        return client


