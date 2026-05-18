from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import get_settings


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker | None = None


def init_db() -> None:
    global engine, async_session_factory
    settings = get_settings()
    engine = create_async_engine(
        settings.postgres_dsn,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.debug,
    )
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    assert async_session_factory is not None, "DB not initialised — call init_db() first"
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
