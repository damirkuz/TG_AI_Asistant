from aiogram.types import Message
from asyncpg import Record
from telethon import TelegramClient
from config_data import DatabaseConfig
from tg_bot.services.database.db_classes import BotUserDB
from tg_bot.services.database import DB


__all__ = [
    "db_create_pool",
    "db_create_need_tables",
    "save_auth",
    "save_bot_user",
    "get_bot_statistics",
    "get_user_tg_id_in_db",
    "get_user_detailed",
    "ban_bot_user",
    "make_admin_bot_user"]


import asyncpg


async def db_create_pool(db_config: DatabaseConfig) -> asyncpg.Pool:
    try:
        return await asyncpg.create_pool(
            user=db_config.db_user,
            password=db_config.db_password,
            database=db_config.database,
            host=db_config.db_host,
            min_size=1,
            max_size=5,
            ssl=None
        )
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")


async def db_create_need_tables(db: DB) -> None:
    # Основная таблица пользователей бота
    await db.execute("""
        CREATE TABLE IF NOT EXISTS bot_users (
            id BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_banned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    # Таблица телеграм-аккаунтов
    await db.execute("""
        CREATE TABLE IF NOT EXISTS tg_accounts (
            id BIGSERIAL PRIMARY KEY,
            tg_user_id BIGINT UNIQUE NOT NULL,
            full_name TEXT,
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    # Таблица сессий
    await db.execute("""
        CREATE TABLE IF NOT EXISTS account_sessions (
            id BIGSERIAL PRIMARY KEY,
            bot_user_id BIGINT REFERENCES bot_users(id) ON DELETE CASCADE,
            tg_account_id BIGINT REFERENCES tg_accounts(id) ON DELETE CASCADE,
            session_data TEXT NOT NULL,
            password TEXT,
            created_at TIMESTAMP DEFAULT now(),
            UNIQUE (bot_user_id, tg_account_id)
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES bot_users(id) ON DELETE CASCADE,
            chat_id BIGINT UNIQUE,
            title TEXT,
            type TEXT,
            last_updated TIMESTAMP
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id BIGSERIAL PRIMARY KEY,
            chat_id BIGINT REFERENCES chats(chat_id) ON DELETE CASCADE,
            user_id BIGINT REFERENCES bot_users(id) ON DELETE SET NULL,
            telegram_id BIGINT,
            text TEXT,
            date TIMESTAMP
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS dossiers (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES bot_users(id) ON DELETE CASCADE,
            target_user_id BIGINT,
            chat_id BIGINT,
            summary_md TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES bot_users(id) ON DELETE CASCADE,
            openai_key TEXT,
            llm_model TEXT
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES bot_users(id),
            action TEXT,
            created_at TIMESTAMP DEFAULT now(),
            details JSONB
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id BIGSERIAL PRIMARY KEY,
            service TEXT,
            key TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES bot_users(id) ON DELETE CASCADE,
            query_text TEXT NOT NULL,
            context_source TEXT,
            context_size INTEGER,
            response_text TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
    """)


async def save_auth(
        client: TelegramClient,
        db: DB,
        session_string: str,
        bot_user_id: int,
        password: str = None
) -> None:
    """
    Сохраняет или обновляет данные аутентификации телеграм-аккаунта в базе данных.

    :param client: Объект TelegramClient для получения информации об аккаунте
    :param db: Объект подключения к базе данных
    :param session_string: Строка сессии телеграм-аккаунта
    :param bot_user_id: ID пользователя бота из таблицы bot_users
    :param password: Пароль для сессии (опционально)

    :raises ValueError: При ошибках сохранения данных или отсутствии аккаунта
    :raises asyncpg.PostgresError: При ошибках работы с базой данных
    """
    try:
        about_me = await client.get_me()

        tg_user_id = int(about_me.id)
        full_name = ' '.join(
            filter(
                None, [
                    about_me.first_name, about_me.last_name])).strip()
        phone_number = about_me.phone

        # Проверка и нормализация номера телефона
        if phone_number:
            phone_number = ''.join(filter(str.isdigit, phone_number)) or None

        # Вставка данных в таблицу телеграм-аккаунтов
        tg_account_row = await db.fetch_one("""
            INSERT INTO tg_accounts (tg_user_id, full_name, phone_number)
            VALUES ($1, $2, $3)
            ON CONFLICT (tg_user_id) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                phone_number = EXCLUDED.phone_number
            RETURNING id
        """, tg_user_id, full_name, phone_number)

        if not tg_account_row:
            raise ValueError("Не удалось сохранить телеграм-аккаунт")

        tg_account_id = tg_account_row["id"]

        # Связывание аккаунта с пользователем бота
        await db.execute("""
            INSERT INTO account_sessions (
                bot_user_id,
                tg_account_id,
                session_data,
                password
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (bot_user_id, tg_account_id) DO UPDATE SET
                session_data = EXCLUDED.session_data,
                password = EXCLUDED.password
        """, bot_user_id, tg_account_id, session_string, password)

    except asyncpg.ForeignKeyViolationError as e:
        raise ValueError(f"Неверный bot_user_id: {bot_user_id}") from e
    except asyncpg.PostgresError as e:
        raise ValueError(f"Ошибка базы данных: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Ошибка сохранения данных: {str(e)}") from e


async def save_bot_user(
        db: DB,
        telegram_id: int,
        full_name: str,
        username: str | None = None,
        is_admin: bool = False,
        is_active: bool = True,
        is_banned: bool = False,
) -> int:
    """
    Сохраняет или обновляет пользователя бота в таблице bot_users.

    :param db: Объект подключения к базе данных
    :param telegram_id: Уникальный идентификатор пользователя в Telegram
    :param full_name: Полное имя пользователя
    :param username: Юзернейм в Telegram (опционально)
    :param is_admin: Флаг администратора (по умолчанию False)
    :param is_active: Флаг активности аккаунта (по умолчанию True)

    :return: ID созданной или обновленной записи
    :raises ValueError: При ошибках сохранения данных
    :raises asyncpg.PostgresError: При ошибках работы с базой данных
    """
    try:
        user_row = await db.fetch_one(
            """
            INSERT INTO bot_users (
                telegram_id,
                full_name,
                username,
                is_admin,
                is_active,
                is_banned
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (telegram_id) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                username = EXCLUDED.username,
                is_active = EXCLUDED.is_active,
                is_banned = EXCLUDED.is_banned
            RETURNING id
            """,
            telegram_id,
            full_name.strip(),
            username,
            is_admin,
            is_active,
            is_banned
        )

        if not user_row:
            raise ValueError("Ошибка при сохранении пользователя")

        return user_row["id"]

    except asyncpg.PostgresError as e:
        raise ValueError(f"Ошибка базы данных: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Неожиданная ошибка: {str(e)}") from e


async def get_bot_statistics(db: DB) -> Record:
    """
    Получает статистику о пользователях бота

    :param db: Объект подключения к базе данных
    :return: Статистика пользователей бота
    """
    return await db.fetch_one("""SELECT
                                (SELECT COUNT(*) FROM bot_users) AS registered_users,
                                (SELECT COUNT(*) FROM tg_accounts) AS connected_accounts,
                                (SELECT COUNT(*) FROM statistics) AS total_activity,
                                (SELECT COUNT(*) FROM statistics WHERE created_at >= NOW() - INTERVAL '1 day') AS daily_activity;
        """)


async def get_user_tg_id_in_db(db: DB, user_message: Message) -> BotUserDB | bool:
    """
    Проверяет есть ли пользователь в базе данных (bot_users), возвращает его BotUserDB

    :param db: Объект подключения к базе данных
    :param user_message: Сообщение пользователя
    :return: Record[telegram_id, is_banned] или False
    """
    from tg_bot.services import get_user_db
    telegram_id = 0
    username = ""
    if user_message.contact:
        telegram_id = user_message.contact.id

    if user_message.text.isdigit():
        telegram_id = int(user_message.text)

    if user_message.text.startswith('@'):
        username = user_message.text.lstrip('@')

    # result = await db.fetch_one("""SELECT telegram_id, is_banned
    #                                    FROM bot_users
    #                                    WHERE telegram_id = $1 OR username = $2
    #                                   """, telegram_id, username)

    bot_user = await get_user_db(telegram_id, username)

    return bot_user if bot_user else False


async def get_user_detailed(db: DB, telegram_id: int) -> dict:
    """
    Возвращает подробную информацию о пользователе из базы

    :param db: Объект подключения к базе данных
    :param telegram_id: Telegram ID запрашиваемого пользователя
    :return: Словарь, содержащий информацию о пользователе и аккаунте прикреплённому им
    """
    result1 = await db.fetch_one("""SELECT *
                                   FROM bot_users
                                   WHERE telegram_id = $1
                                    """, telegram_id)
    bot_user_id = result1["id"]

    result2 = await db.fetch_one("""SELECT *
                                       FROM tg_accounts
                                       WHERE id = $1
                                        """, bot_user_id)

    if result2:
        merged = {
            "bot_user": {
                "id": result1["id"],
                "telegram_id": result1["telegram_id"],
                "username": result1["username"],
                "full_name": result1["full_name"],
                "is_admin": result1["is_admin"],
                "is_active": result1["is_active"],
                "is_banned": result1["is_banned"],
                "created_at": result1["created_at"],
            },
            "tg_account": {
                "id": result2["id"],
                "tg_user_id": result2["tg_user_id"],
                "full_name": result2["full_name"],
                "phone_number": result2["phone_number"],
                "created_at": result2["created_at"],
            }
        }
    else:
        merged = {"bot_user": dict(result1), "tg_account": None}

    return merged


async def ban_bot_user(db: DB, telegram_id: int, ban: bool = True) -> None:
    from tg_bot.middlewares.ban_check_middleware import BanCheckMiddleware
    BanCheckMiddleware.clear_user_cache(telegram_id)
    await db.execute("""UPDATE bot_users
                        SET is_banned = $1
                        WHERE telegram_id = $2
                    """, ban, telegram_id)


async def make_admin_bot_user(db: DB, telegram_id: int, make_admin: bool = True) -> None:
    await db.execute("""UPDATE bot_users
                        SET is_admin = $1
                        WHERE telegram_id = $2
                    """, make_admin, telegram_id)