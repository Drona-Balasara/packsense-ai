"""
Shared pytest fixtures for PackSense AI backend tests.

Uses an in-memory SQLite database so tests are:
  - isolated (each test session gets a fresh DB)
  - fast (no file I/O)
  - side-effect free (never touches packsense.db)
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.connection import get_session
from app.database.seed import run_seed
from app.main import create_app
from app.models.base import Base

# ── In-memory test database ────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create all tables and seed data once per test session."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSessionLocal() as db:
        await run_seed(db)

    yield

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Yield a fresh async session for a single test, rolled back on teardown."""
    async with _TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """
    Async HTTP test client wired to the FastAPI app with the test DB injected.
    The get_session dependency is overridden to use the in-memory test database.
    """
    app = create_app()

    async def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
