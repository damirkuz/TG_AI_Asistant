from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from tg_bot.lexicon import LEXICON_BUTTONS_RU
from typing import Optional


def create_inline_kb(
        *args: str,
        width: int = 1,
        last_button: Optional[str] = None,
        **kwargs: dict[str, str]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if args:
        for button in args:
            buttons.append(
                InlineKeyboardButton(
                    text=LEXICON_BUTTONS_RU[button] if button in LEXICON_BUTTONS_RU else button,
                    callback_data=button))

    if kwargs:
        for button, text in kwargs.items():
            buttons.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=button))

    kb_builder.row(*buttons, width=width)

    if last_button is not None:
        kb_builder.row(
            InlineKeyboardButton(
                text=last_button,
                callback_data='last_button'))
    return kb_builder.as_markup(resize_keyboard=True)


def create_reply_kb(
        *args: str | list[KeyboardButton] | KeyboardButton,
        width: int = 1) -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons: list[KeyboardButton] = []

    if args:
        for button in args:
            if isinstance(button, list):
                buttons.extend(button)
            elif isinstance(button, KeyboardButton):
                buttons.append(button)
            else:
                buttons.append(KeyboardButton(text=LEXICON_BUTTONS_RU[button]))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup(resize_keyboard=True)
