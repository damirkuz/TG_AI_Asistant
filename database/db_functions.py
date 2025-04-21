import asyncpg
from asyncpg import Pool
from telethon import TelegramClient

from config_data import DatabaseConfig

__all__ = ["db_create_pool", "db_execute_sql", "db_create_need_tables", "save_auth"]


async def db_create_pool(db_config: DatabaseConfig) -> Pool:
    try:
        return await asyncpg.create_pool(
            user=db_config.db_user,
            password=db_config.db_password,
            database=db_config.database,
            host=db_config.db_host,
            min_size=1,  # Минимальное количество соединений
            max_size=5,  # Максимальное количество соединений
            ssl=None
        )
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")

async def db_execute_sql(db_pool: Pool, sql: str, *args, **kwargs) -> None:
    async with db_pool.acquire() as conn:
        await conn.execute(sql, *args)


async def db_create_need_tables(db_pool: Pool) -> None:

    # Создание таблицы пользователей
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            phone_number BIGINT,         -- Номер телефона
            password TEXT,               -- Лучше хранить зашифрованным
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    # Создание таблицы сессий
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            session_path TEXT,           -- Путь к .session-файлу
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    # Создание таблицы чатов
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            chat_id BIGINT UNIQUE,       -- ID чата из Telegram
            title TEXT,
            type TEXT,                   -- Тип: private / group / supergroup / channel
            last_updated TIMESTAMP
        );
    """)

    # Создание таблицы сообщений
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS messages (
            id BIGSERIAL PRIMARY KEY,
            chat_id BIGINT REFERENCES chats(chat_id) ON DELETE CASCADE,
            user_id BIGINT REFERENCES users(id) ON DELETE SET NULL, -- автор сообщения
            telegram_id BIGINT,             -- ID сообщения в Telegram
            text TEXT,
            date TIMESTAMP
        );
    """)

    # Создание таблицы досье
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS dossiers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- кто создавал
            target_user_id BIGINT,           -- на кого создавали досье (по Telegram ID)
            chat_id BIGINT,                  -- ID чата, где анализировались сообщения
            summary_md TEXT,                 -- Итог анализа в формате Markdown
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    # Создание таблицы настроек пользователя
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            openai_key TEXT,                 -- Пользовательский ключ OpenAI (шифровать!)
            llm_model TEXT                   -- Используемая модель (например, gpt-4)
        );
    """)

    # Создание таблицы статистики использования
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS statistics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            action TEXT,                     -- Действие: команда или операция
            created_at TIMESTAMP DEFAULT now(),
            details JSONB                    -- Доп. параметры запроса: чат, модель и т.д.
        );
    """)

    # Создание таблицы API-ключей
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            service TEXT,                    -- Название сервиса (например: openai)
            key TEXT,                        -- Ключ (зашифровать на Python-стороне)
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP
        );
    """)

    # Создание таблицы запросов пользователя к ИИ
    await db_execute_sql(db_pool=db_pool, sql="""
        CREATE TABLE IF NOT EXISTS queries (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            query_text TEXT NOT NULL,        -- Вопрос, заданный пользователем
            context_source TEXT,             -- Откуда взят контекст (chat, dossier и т.д.)
            context_size INTEGER,            -- Сколько сообщений использовалось
            response_text TEXT,              -- Ответ от нейросети
            model_used TEXT,                 -- Название модели (gpt-4, mistral и т.д.)
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    # старая бд
    # # Создание таблицы пользователей
    # await db_execute_sql(db_pool=db_pool, sql="""
    #     CREATE TABLE IF NOT EXISTS users (
    #         user_id BIGINT PRIMARY KEY,  -- ID пользователя (совпадает с Telegram ID)
    #         username TEXT UNIQUE,        -- Username (если есть)
    #         first_name TEXT,             -- Имя
    #         last_name TEXT,              -- Фамилия
    #         session_path TEXT,           -- Путь до сессии телеграмм
    #         phone_number BIGINT,         -- Номер телефона
    #         password TEXT,
    #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата регистрации в боте
    #     );
    # """)
    #
    # # Создание таблицы чатов
    # await db_execute_sql(db_pool=db_pool, sql="""
    #     CREATE TABLE IF NOT EXISTS chats (
    #         chat_id BIGINT PRIMARY KEY,  -- ID чата (Telegram ID)
    #         chat_title TEXT,             -- Название чата
    #         chat_type TEXT CHECK (chat_type IN ('private', 'group', 'supergroup', 'channel')),  -- Тип чата
    #         user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,  -- Ссылаемся на пользователя, связанного с чатом
    #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата создания чата
    #     );
    # """)
    #
    # # Создание таблицы сообщений
    # await db_execute_sql(db_pool=db_pool, sql="""
    #     CREATE TABLE IF NOT EXISTS messages (
    #         message_id BIGINT PRIMARY KEY, -- ID сообщения
    #         chat_id BIGINT REFERENCES chats(chat_id) ON DELETE CASCADE,  -- Чат, к которому относится сообщение
    #         user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL, -- Автор сообщения
    #         text TEXT,               -- Текст сообщения
    #         timestamp TIMESTAMP,      -- Время отправки
    #         embedding VECTOR(1536)    -- Векторное представление текста (если используем pgvector для поиска)
    #     );
    # """)
    #
    # # Создание таблицы запросов
    # await db_execute_sql(db_pool=db_pool, sql="""
    #     CREATE TABLE IF NOT EXISTS queries (
    #         query_id SERIAL PRIMARY KEY,
    #         user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,  -- Кто сделал запрос
    #         query_text TEXT,         -- Текст запроса
    #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #         response_text TEXT       -- Ответ AI
    #     );
    # """)
    #
    # # Таблица кэша
    # await db_execute_sql(db_pool=db_pool, sql="""
    #     CREATE TABLE IF NOT EXISTS cache (
    #         query_hash TEXT PRIMARY KEY, -- Хэш от запроса (чтобы не хранить дубли)
    #         response_text TEXT,          -- Закешированный ответ
    #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #     );
    # """)


async def save_auth(client: TelegramClient, db_pool: Pool, session_path: str, password: str = None) -> None:
    # TODO Реализовать сохранение данных в базу
    pass
    # about_me = await client.get_me()
    # username = about_me.username
    # user_id = int(about_me.id)
    # first_name = about_me.first_name
    # last_name = about_me.last_name
    # phone_number = int(about_me.phone)
    # sql_request = """
    # INSERT INTO users (user_id, username, first_name, last_name, session_path, phone_number, password)
    # VALUES ($1, $2, $3, $4, $5, $6, $7)
    # ON CONFLICT (user_id)
    # DO UPDATE SET
    #     username = EXCLUDED.username,
    #     first_name = EXCLUDED.first_name,
    #     last_name = EXCLUDED.last_name,
    #     session_path = EXCLUDED.session_path,
    #     phone_number = EXCLUDED.phone_number,
    #     password = EXCLUDED.password;"""
    # await db_execute_sql(db_pool, sql_request, user_id, username, first_name, last_name, session_path, phone_number, password)





