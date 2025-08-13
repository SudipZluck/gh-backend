import os
from typing import Iterator

from fastapi import Request
from sqlmodel import Session, create_engine


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    return ""


def build_mysql_url() -> str:
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name = _require_env("DB_NAME")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"


def create_engine_from_env():
    url = build_mysql_url()
    print( url)
    return create_engine(url, pool_pre_ping=True)


def dispose_engine(engine) -> None:
    engine.dispose()


def get_session(request: Request) -> Iterator[Session]:
    session_factory = request.app.state.sql_session_factory
    with session_factory() as session:
        yield session