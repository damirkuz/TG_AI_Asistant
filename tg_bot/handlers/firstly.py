import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import DB
from tg_bot.keyboards import main_menu_keyboard, main_menu_admin_keyboard
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.services import get_user_db
from tg_bot.states import FSMMainMenu

__all__ = ['router']

router = Router()

logger = logging.getLogger(__name__)


@router.message(F.text == LEXICON_BUTTONS_RU['back_to_main_menu'])
async def process_accept_rules(message: Message, state: FSMContext, db: DB):
    logger.info("Пользователь %s (%d) выбрал возврат в главное меню", message.from_user.username, message.from_user.id)
    user_db = await get_user_db(db=db, user_id=message.from_user.id)
    if user_db.is_admin:
        logger.debug("Пользователь %s (%d) является админом, отправляется админ-меню", message.from_user.username,
                     message.from_user.id)
        await message.answer(LEXICON_ANSWERS_RU['back_to_main_menu'], reply_markup=main_menu_admin_keyboard)
    else:
        logger.debug("Пользователь %s (%d) не является админом, отправляется обычное меню", message.from_user.username,
                     message.from_user.id)
        await message.answer(LEXICON_ANSWERS_RU['back_to_main_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(FSMMainMenu.waiting_choice)
    logger.debug("FSMMainMenu: переведено в waiting_choice для пользователя %d", message.from_user.id)
