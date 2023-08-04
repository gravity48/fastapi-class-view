import os
from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from example.settings import database_settings

Base = declarative_base()


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=MetaSingleton):
    def __init__(self):
        self._engine = create_async_engine(
            f"postgresql+asyncpg://django:django@localhost:5432/{database_settings.PATH}",
            echo=True,
        )
        self._session_factory = async_scoped_session(
            async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False),
            scopefunc=current_task,
        )

    @staticmethod
    async def create_database(db_name) -> None:
        engine = create_async_engine(
            "postgresql+asyncpg://django:django@localhost:5432/postgres",
            echo=True,
        )
        conn = await engine.connect()
        try:
            await conn.execute(text('COMMIT'))
            await conn.execute(text(f'CREATE DATABASE {db_name}'))
        finally:
            await conn.close()

    @staticmethod
    async def drop_database(db_name) -> None:
        engine = create_async_engine(
            "postgresql+asyncpg://django:django@localhost:5432/postgres",
            echo=True,
        )
        conn = await engine.connect()
        try:
            await conn.execute(text('COMMIT'))
            await conn.execute(text(f'DROP DATABASE {db_name} WITH (FORCE)'))
        finally:
            await conn.close()

    def setup_database(self, path):
        self._engine = create_async_engine(
            f"postgresql+asyncpg://django:django@localhost:5432/{path}",
            echo=True,
        )
        self._session_factory = async_scoped_session(
            async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self):
        session: AsyncSession = self._session_factory()
        try:
            yield session
            if not os.getenv('DEBUG'):
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
