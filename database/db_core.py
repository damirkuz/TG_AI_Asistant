from typing import Any, Optional

from asyncpg import Pool, Record

__all__ = ["DB"]

class DB:

    def __init__(self, pool: Pool):
        self.pool = pool

    async def execute(self, sql: str, *args) -> str:
        """Выполнить SQL-запрос без возврата результата"""
        async with self.pool.acquire() as conn:
            return await conn.execute(sql, *args)

    async def fetch_one(self, sql: str, *args) -> Optional[Record]:
        """Получить одну строку результата"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    async def fetch_val(self, sql: str, *args) -> Any:
        """Получить одно значение (первую ячейку результата)"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql, *args)

    async def fetch_all(self, sql: str, *args) -> list[Record]:
        """Получить список строк результата"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)