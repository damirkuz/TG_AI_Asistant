import logging

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import save_bot_user
from database.db_classes import BotUserDB
from tg_bot.filters import IsRegistered
from tg_bot.keyboards import create_reply_kb, main_menu_keyboard, settings_add_telegram_keyboard
from tg_bot.keyboards.reply_keyboards import main_menu_admin_keyboard
from tg_bot.lexicon import LEXICON_ANSWERS_RU, LEXICON_BUTTONS_RU
from tg_bot.states import FSMRulesAgreement, FSMMainMenu, FSMSettingsState

__all__ = ['router']

router = Router()

logger = logging.getLogger(__name__)


@router.message(CommandStart(), IsRegistered())
async def process_start_command(message: Message, state: FSMContext, user_db: BotUserDB):
    logger.info("Пользователь %s (%d) выполнил /start и зарегистрирован (is_admin=%s)", message.from_user.username,
                message.from_user.id, user_db.is_admin)
    if user_db.is_admin:
        await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_admin_keyboard)
        logger.debug("Пользователь %s (%d) получил админ-меню", message.from_user.username, message.from_user.id)
    else:
        await message.answer(text=LEXICON_ANSWERS_RU['/start'], reply_markup=main_menu_keyboard)
        logger.debug("Пользователь %s (%d) получил обычное меню", message.from_user.username, message.from_user.id)
    await state.set_state(FSMMainMenu.waiting_choice)
    logger.debug("FSMMainMenu: переведено в waiting_choice для пользователя %d", message.from_user.id)


# сюда попадёт новый пользователь
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    logger.info("Новый пользователь %s (%d) выполнил /start", message.from_user.username, message.from_user.id)
    keyboard_now = create_reply_kb('accept_rules')
    await message.answer(text=LEXICON_ANSWERS_RU['/start'])
    await message.answer(text=LEXICON_ANSWERS_RU['agree_rules'], reply_markup=keyboard_now,
                         parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(FSMRulesAgreement.waiting_for_agree)
    logger.debug("FSMRulesAgreement: переведено в waiting_for_agree для пользователя %d", message.from_user.id)


# согласие с правилами реализую здесь, так как это единичная операция и
# логично оставить её там, где вызывается.
@router.message(StateFilter(FSMRulesAgreement.waiting_for_agree),
                F.text == LEXICON_BUTTONS_RU['accept_rules'])
async def process_accept_rules(message: Message, state: FSMContext):
    logger.info("Пользователь %s (%d) согласился с правилами", message.from_user.username, message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['accept_success'])
    # сохраняем пользователя в бд
    bot_user_id = await save_bot_user(telegram_id=message.from_user.id, full_name=message.from_user.full_name,
                                      username=message.from_user.username)
    logger.debug("Пользователь %s (%d) сохранён в базе с bot_user_id=%s", message.from_user.username,
                 message.from_user.id, bot_user_id)
    await state.update_data(bot_user_id=bot_user_id)
    await state.set_state(FSMSettingsState.waiting_choice)
    logger.debug("FSMSettingsState: переведено в waiting_choice для пользователя %d", message.from_user.id)
    await message.answer(text=LEXICON_ANSWERS_RU['settings_add_telegram_menu'],
                         reply_markup=settings_add_telegram_keyboard)
    logger.debug("Пользователю %d отправлено меню добавления Telegram-аккаунта", message.from_user.id)


# запустится, если пользователь не принял правила
@router.message(StateFilter(FSMRulesAgreement.waiting_for_agree))
async def process_accept_rules(message: Message):
    logger.warning("Пользователь %s (%d) не согласился с правилами, повторный запрос", message.from_user.username,
                   message.from_user.id)
    keyboard_now = create_reply_kb('accept_rules')
    await message.answer(text=LEXICON_ANSWERS_RU['accept_retry'], reply_markup=keyboard_now)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    logger.info("Пользователь %s (%d) вызвал /help", message.from_user.username, message.from_user.id)
    await message.answer(LEXICON_ANSWERS_RU['/help'])
