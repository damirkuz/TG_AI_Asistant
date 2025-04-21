import telethon
import os
import asyncio

from asyncpg import Pool
from telethon import TelegramClient
import telethon.errors
from config_data import TGAppConfig
import datetime
from enum import Enum
from database import db_execute_sql


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
    os.makedirs("users_tg_sessions", exist_ok=True)

    session_path = f"users_tg_sessions/main_session_{user_id}_{
        datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    client = TelegramClient(
        session_path,
        tg_app_config.api_id,
        tg_app_config.api_hash)
    await client.connect()

    while True:
        try:
            await client.send_code_request(phone)
            return {'tg_client': client, 'session_path': session_path}
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


async def fetch_messages(client: TelegramClient, chat_id: int | str) -> list:
    messages = []
    chat = await client.get_input_entity(chat_id)  # получаем сущность по ID
    async for message in client.iter_messages(entity=chat, reverse=True):
        print(message.text)
        messages.append(message)
        # Пауза между запросами (уменьшает риск блокировки)
        await asyncio.sleep(0.5)
    return messages
