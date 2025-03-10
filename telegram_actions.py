import telethon
import os
import asyncio
from telethon import TelegramClient
import telethon.errors
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




async def auth_send_code(tg_app_config: TGAppConfig, user_id: str, phone: str) -> AuthStatesEnum | dict[str, TelegramClient | str]:
    # Создаём папку для сессий
    os.makedirs("users_tg_sessions", exist_ok=True)

    session_path = f"users_tg_sessions/main_session_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    client = TelegramClient(session_path, tg_app_config.api_id, tg_app_config.api_hash)
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


async def auth_enter_code(client: TelegramClient, phone: str, code: str) -> AuthStatesEnum:
    try:
        await client.sign_in(phone=phone, code=code)
        return AuthStatesEnum.CodeValid
    except telethon.errors.PhoneCodeInvalidError:
        return AuthStatesEnum.CodeInvalid
    except telethon.errors.PhoneCodeExpiredError:
        return AuthStatesEnum.CodeExpired
    except telethon.errors.SessionPasswordNeededError:
        return AuthStatesEnum.PasswordNeeded


async def auth_enter_password(client: TelegramClient, password: str) -> AuthStatesEnum:
    try:
        await client.sign_in(password=password)
        return AuthStatesEnum.PasswordValid
    except telethon.errors.PasswordHashInvalidError:
        return AuthStatesEnum.PasswordInvalid



async def save_auth(client: TelegramClient, session_path: str,  phone: str, password: str = None) -> None:
    # TODO Реализовать сохранение данных в базу
    print(session_path, phone, password)


# async def get_phone() -> str:
#     return await asyncio.to_thread(input, "Введите телефон: ")
#
#
# async def get_code() -> str:
#     return await asyncio.to_thread(input, "Введите код из Telegram: ")
#
#
# async def get_password() -> str:
#     return await asyncio.to_thread(input, "Введите пароль: ")



# async def login_tg(tg_app_config: TGAppConfig, user_id: str) -> TelegramClient:
#
#     # Создаём папку для сессий
#     os.makedirs("users_tg_sessions", exist_ok=True)
#
#     session_path = f"users_tg_sessions/main_session_{user_id}"
#     client = TelegramClient(session_path, tg_app_config.api_id, tg_app_config.api_hash)
#     await client.connect()
#
#     if await client.is_user_authorized():
#         print("✅ Уже авторизован!")
#         return client
#
#     phone = await get_phone()
#
#     # Запрашиваем код подтверждения
#     try:
#         result = await client.send_code_request(phone)
#     except telethon.errors.FloodWaitError as e:
#         print(f"⚠️ Слишком много запросов! Ждём {e.seconds} секунд...")
#         await asyncio.sleep(e.seconds)
#     except telethon.errors.PhoneNumberInvalidError:
#         print("❌ Ошибка: Неправильный номер телефона!")
#         return None
#     except telethon.errors.PhoneNumberBannedError:
#         print("❌ Ошибка: Этот номер забанен в Telegram!")
#         return None
#
#     # Вводим код с обработкой ошибок
#     while True:
#         code = await get_code()
#         try:
#             await client.sign_in(phone=phone, code=code)
#             break
#         except telethon.errors.PhoneCodeInvalidError:
#             print("❌ Ошибка: Неправильный код! Попробуйте ещё раз.")
#         except telethon.errors.PhoneCodeExpiredError:
#             print("⚠️ Ошибка: Код устарел! Запрашиваю новый...")
#             await client.send_code_request(phone)
#         except telethon.errors.SessionPasswordNeededError:
#             # Если нужен пароль
#             while True:
#                 password = await get_password()
#                 try:
#                     await client.sign_in(password=password)
#                     break
#                 except telethon.errors.PasswordHashInvalidError:
#                     print("❌ Ошибка: Неправильный пароль! Попробуйте ещё раз.")
#             break
#
#
#     print("✅ Авторизация успешна!")
#     return client



async def fetch_messages(client: TelegramClient, chat_id: int | str) -> list:
    messages = []
    chat = await client.get_input_entity(chat_id)  # получаем сущность по ID
    async for message in client.iter_messages(entity=chat, reverse=True):
        print(message.text)
        messages.append(message)
        # Пауза между запросами (уменьшает риск блокировки)
        await asyncio.sleep(0.5)
    return messages
