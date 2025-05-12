import logging

from aiogram import Router
from aiogram.types import Message

from tg_bot.lexicon import LEXICON_ANSWERS_RU

__all__ = ['router']

router = Router()

logger = logging.getLogger(__name__)


@router.message()
async def process_other_messages(message: Message):
    logger.info("Пользователь %s (%d) отправил неизвестное сообщение: %s", message.from_user.username,
                message.from_user.id, message.text)
    await message.answer(LEXICON_ANSWERS_RU['other_messages'])
