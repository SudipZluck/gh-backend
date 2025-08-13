import os
from typing import AsyncIterator

import aiomysql
from fastapi import Request


def _get_int_env(name: str, default_value: int) -> int:
    try:
        return int(os.getenv(name, str(default_value)))
    except ValueError:
        return default_value


async def create_pool() -> aiomysql.Pool:
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = _get_int_env("DB_PORT", 3306)
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "")
    maxsize = _get_int_env("DB_POOL_MAXSIZE", 10)

    return await aiomysql.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db_name or None,
        autocommit=True,
        minsize=1,
        maxsize=maxsize,
        charset="utf8mb4",
    )


async def close_pool(pool: aiomysql.Pool) -> None:
    pool.close()
    await pool.wait_closed()


async def get_db_connection(request: Request) -> AsyncIterator[aiomysql.Connection]:
    pool: aiomysql.Pool = request.app.state.mysql_pool
    async with pool.acquire() as connection:
        yield connection