from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy import VARCHAR, Column, Integer
from sqlalchemy.ext.asyncio import (
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


class UsersModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(50))
    first_name = Column(VARCHAR(100))
    last_name = Column(VARCHAR(100))


class Database(metaclass=MetaSingleton):
    def __init__(self):
        self._engine = create_async_engine(
            f"sqlite+aiosqlite:///{database_settings.PATH}",
            echo=True,
        )
        self._session_factory = async_scoped_session(
            async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False),
            scopefunc=current_task,
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self):
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
