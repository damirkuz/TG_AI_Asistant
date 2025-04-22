
from asyncpg import Pool
from telethon import TelegramClient
from config_data import DatabaseConfig
from tg_bot.services.database import DB


__all__ = ["db_create_pool", "db_create_need_tables", "save_auth"]


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
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            phone_number BIGINT,
            password TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            session_path TEXT,
            created_at TIMESTAMP DEFAULT now(),
            UNIQUE (user_id, session_path)
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
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
            user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            telegram_id BIGINT,
            text TEXT,
            date TIMESTAMP
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS dossiers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            target_user_id BIGINT,
            chat_id BIGINT,
            summary_md TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            openai_key TEXT,
            llm_model TEXT
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            action TEXT,
            created_at TIMESTAMP DEFAULT now(),
            details JSONB
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            service TEXT,
            key TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            query_text TEXT NOT NULL,
            context_source TEXT,
            context_size INTEGER,
            response_text TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
    """)



async def save_auth(client: TelegramClient, db: DB, session_path: str, password: str = None) -> None:
    about_me = await client.get_me()

    telegram_id = int(about_me.id)
    username = about_me.username
    full_name = (about_me.first_name or "") + " " + (about_me.last_name or "")
    phone_number = int(about_me.phone)

    user_row = await db.fetch_one("""
        INSERT INTO users (telegram_id, username, full_name, phone_number, password)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (telegram_id) DO UPDATE
        SET username = EXCLUDED.username,
            full_name = EXCLUDED.full_name,
            phone_number = EXCLUDED.phone_number,
            password = EXCLUDED.password
        RETURNING id
    """, telegram_id, username, full_name, phone_number, password)

    if user_row is None:
        raise ValueError("Пользователь не был сохранён")

    user_id = user_row["id"]

    await db.execute("""
        INSERT INTO sessions (user_id, session_path)
        VALUES ($1, $2)
    """, user_id, session_path)
