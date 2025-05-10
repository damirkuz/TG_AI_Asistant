import logging
from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from tg_bot.lexicon import LEXICON_BUTTONS_RU

logger = logging.getLogger(__name__)


def create_inline_kb(
        *args: str,
        width: int = 1,
        last_button: Optional[str] = None,
        **kwargs: dict[str, str]) -> InlineKeyboardMarkup:
    logger.info("Создание inline-клавиатуры: args=%s, width=%d, last_button=%s, kwargs=%s", args, width, last_button,
                kwargs)
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if args:
        for button in args:
            btn_text = LEXICON_BUTTONS_RU[button] if button in LEXICON_BUTTONS_RU else button
            logger.debug("Добавление кнопки: text=%s, callback_data=%s", btn_text, button)
            buttons.append(
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=button))

    if kwargs:
        for button, text in kwargs.items():
            logger.debug("Добавление кнопки через kwargs: text=%s, callback_data=%s", text, button)
            buttons.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=button))

    kb_builder.row(*buttons, width=width)

    if last_button is not None:
        logger.debug("Добавление последней кнопки: text=%s, callback_data=last_button", last_button)
        kb_builder.row(
            InlineKeyboardButton(
                text=last_button,
                callback_data='last_button'))
    markup = kb_builder.as_markup(resize_keyboard=True)
    logger.debug("Inline-клавиатура создана: %s", markup)
    return markup


def create_reply_kb(
        *args: str | list[KeyboardButton] | KeyboardButton,
        width: int = 1) -> ReplyKeyboardMarkup:
    logger.info("Создание reply-клавиатуры: args=%s, width=%d", args, width)
    kb_builder = ReplyKeyboardBuilder()
    buttons: list[KeyboardButton] = []

    if args:
        for button in args:
            if isinstance(button, list):
                logger.debug("Добавление списка кнопок: %s", button)
                buttons.extend(button)
            elif isinstance(button, KeyboardButton):
                logger.debug("Добавление кнопки KeyboardButton: %s", button)
                buttons.append(button)
            else:
                logger.debug("Добавление кнопки по ключу: %s", button)
                buttons.append(KeyboardButton(text=LEXICON_BUTTONS_RU[button]))

    kb_builder.row(*buttons, width=width)

    markup = kb_builder.as_markup(resize_keyboard=True)
    logger.debug("Reply-клавиатура создана: %s", markup)
    return markup
