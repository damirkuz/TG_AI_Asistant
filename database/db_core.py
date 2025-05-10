from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config_data.config import get_database_url

__all__ = ["Base", "async_session_maker"]

DATABASE_URL = get_database_url()

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)
# Фабрика сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Шаблон именования ограничений для Alembic
convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata

# class DB:
#
#     def __init__(self, pool: Pool):
#         self.pool = pool
#
#     async def execute(self, sql: str, *args) -> str:
#         """Выполнить SQL-запрос без возврата результата"""
#         async with self.pool.acquire() as conn:
#             return await conn.execute(sql, *args)
#
#     async def fetch_one(self, sql: str, *args) -> Optional[Record]:
#         """Получить одну строку результата"""
#         async with self.pool.acquire() as conn:
#             return await conn.fetchrow(sql, *args)
#
#     async def fetch_val(self, sql: str, *args) -> Any:
#         """Получить одно значение (первую ячейку результата)"""
#         async with self.pool.acquire() as conn:
#             return await conn.fetchval(sql, *args)
#
#     async def fetch_all(self, sql: str, *args) -> list[Record]:
#         """Получить список строк результата"""
#         async with self.pool.acquire() as conn:
#             return await conn.fetch(sql, *args)
