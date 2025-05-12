import asyncio
import logging
from enum import Enum

import telethon
import telethon.errors
from telethon import TelegramClient
from telethon.sessions import StringSession

from config_data.config import TGAppConfig

logger = logging.getLogger(__name__)

__all__ = ["auth_send_code", "auth_enter_code", "auth_enter_password", "AuthStatesEnum"]


class AuthStatesEnum(Enum):
    PhoneNumberBanned = "PhoneNumberBanned",
    CodeSent = "CodeSent",
    CodeValid = "CodeValid",
    CodeInvalid = "CodeInvalid",
    CodeExpired = "CodeExpired",
    PasswordNeeded = "PasswordNeeded",
    PasswordValid = "PasswordValid",
    PasswordInvalid = "PasswordInvalid"


async def auth_send_code(tg_app_config: TGAppConfig,
                         user_id: str,
                         phone: str) -> (AuthStatesEnum
                                         | dict[str, TelegramClient | str]):
    logger.info("Начало отправки кода авторизации на номер %s для user_id=%s", phone, user_id)
    session = StringSession()
    client = TelegramClient(
        session,
        tg_app_config.api_id,
        tg_app_config.api_hash)
    await client.connect()

    while True:
        try:
            await client.send_code_request(phone)
            session_string = client.session.save()
            logger.info("Код успешно отправлен на номер %s для user_id=%s", phone, user_id)
            return {'tg_client': client, 'session_string': session_string}
        except telethon.errors.FloodWaitError as e:
            logger.warning("FloodWaitError при отправке кода на номер %s: ждём %d секунд", phone, e.seconds)
            print(f"⚠️ Слишком много запросов! Ждём {e.seconds} секунд...")
            await asyncio.sleep(e.seconds)
        except telethon.errors.PhoneNumberBannedError:
            logger.error("Номер %s забанен при попытке отправки кода для user_id=%s", phone, user_id)
            return AuthStatesEnum.PhoneNumberBanned


async def auth_enter_code(
        client: TelegramClient,
        phone: str,
        code: str) -> AuthStatesEnum:
    logger.info("Попытка входа по коду для номера %s", phone)
    try:
        await client.sign_in(phone=phone, code=code)
        logger.info("Код подтверждён для номера %s", phone)
        return AuthStatesEnum.CodeValid
    except telethon.errors.PhoneCodeInvalidError:
        logger.warning("Введён неверный код для номера %s", phone)
        return AuthStatesEnum.CodeInvalid
    except telethon.errors.PhoneCodeExpiredError:
        logger.warning("Введён просроченный код для номера %s", phone)
        return AuthStatesEnum.CodeExpired
    except telethon.errors.SessionPasswordNeededError:
        logger.info("Для номера %s требуется пароль", phone)
        return AuthStatesEnum.PasswordNeeded


async def auth_enter_password(
        client: TelegramClient,
        password: str) -> AuthStatesEnum:
    logger.info("Попытка входа по паролю через TelegramClient")
    try:
        await client.sign_in(password=password)
        logger.info("Пароль подтверждён")
        return AuthStatesEnum.PasswordValid
    except telethon.errors.PasswordHashInvalidError:
        logger.warning("Введён неверный пароль")
        return AuthStatesEnum.PasswordInvalid
