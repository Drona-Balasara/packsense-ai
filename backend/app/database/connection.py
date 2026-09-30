"""
Database connection and session management.

Uses SQLAlchemy async engine so the same code works with:
  - SQLite  (sqlite+aiosqlite:///./<file>.db)   ← local dev default
  - PostgreSQL (postgresql+asyncpg://...)        ← production target

The engine and session factory are created once at import time from Settings.
Use `get_session()` as a FastAPI dependency.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.models.base import Base

_settings = get_settings()

# ── Engine ─────────────────────────────────────────────────────────────────────
# echo=True logs all SQL in development; disable in production.
engine: AsyncEngine = create_async_engine(
    _settings.database_url,
    echo=_settings.app_debug,
    future=True,
    # SQLite specific: allow usage across threads (needed for async SQLite)
    connect_args={"check_same_thread": False}
    if "sqlite" in _settings.database_url
    else {},
)

# ── Session factory ────────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def create_all_tables() -> None:
    """Create all tables defined in ORM models. Called on application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables() -> None:
    """Drop all tables — use only in tests or explicit reset operations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
