"""Async database session factory with connection pooling."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from stock_agent.config.settings import get_settings

_engine = None
_session_factory = None


def _get_engine():
    """Lazily create the async engine with connection pool settings."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.SUPABASE_DB_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=(settings.APP_ENV == "development"),
            # Supabase uses pgBouncer (transaction mode) which conflicts with
            # asyncpg's prepared statement caching → disable it
            connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
        )
    return _engine


def _get_session_factory():
    """Lazily create the session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=_get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional async database session.

    Usage:
        async with get_session() as session:
            result = await session.execute(select(Model))
    """
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
