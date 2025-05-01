import telethon
import os
import asyncio

from asyncpg import Pool
from telethon import TelegramClient
import telethon.errors
from telethon.sessions import StringSession

from config_data import TGAppConfig
import datetime
from enum import Enum


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
                         phone: str) -> AuthStatesEnum | dict[str,
                                                              TelegramClient | str]:
    # Создаём папку для сессий
    # os.makedirs("../../users_tg_sessions", exist_ok=True)
    #
    # session_path = f"users_tg_sessions/main_session_{user_id}_{
    #     datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    # client = TelegramClient(
    #     session_path,
    #     tg_app_config.api_id,
    #     tg_app_config.api_hash)
    # await client.connect()

    session = StringSession()
    client = TelegramClient(session, tg_app_config.api_id, tg_app_config.api_hash)
    await client.connect()


    while True:
        try:
            await client.send_code_request(phone)
            session_string = client.session.save()
            return {'tg_client': client, 'session_string': session_string}
        except telethon.errors.FloodWaitError as e:
            print(f"⚠️ Слишком много запросов! Ждём {e.seconds} секунд...")
            await asyncio.sleep(e.seconds)
        except telethon.errors.PhoneNumberBannedError:
            return AuthStatesEnum.PhoneNumberBanned


async def auth_enter_code(
        client: TelegramClient,
        phone: str,
        code: str) -> AuthStatesEnum:
    try:
        await client.sign_in(phone=phone, code=code)
        return AuthStatesEnum.CodeValid
    except telethon.errors.PhoneCodeInvalidError:
        return AuthStatesEnum.CodeInvalid
    except telethon.errors.PhoneCodeExpiredError:
        return AuthStatesEnum.CodeExpired
    except telethon.errors.SessionPasswordNeededError:
        return AuthStatesEnum.PasswordNeeded


async def auth_enter_password(
        client: TelegramClient,
        password: str) -> AuthStatesEnum:
    try:
        await client.sign_in(password=password)
        return AuthStatesEnum.PasswordValid
    except telethon.errors.PasswordHashInvalidError:
        return AuthStatesEnum.PasswordInvalid