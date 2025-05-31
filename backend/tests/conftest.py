import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator
from sqlmodel import SQLModel

from src.main import app
from src.auth.dependencies import get_db
from src.config import settings

# Use SQLite in memory for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create a test session
async_test_session = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Session fixture
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Import the models here to ensure they're registered with SQLModel
    from src.models import User, Project, SharedProject
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Create session
    async with async_test_session() as session:
        try:
            yield session
        finally:
            await session.close()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# Override get_db dependency
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_test_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Dependency override
@pytest.fixture
def app_with_db_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


# Setup database before API tests
@pytest_asyncio.fixture
async def setup_db():
    # Import the models here to ensure they're registered with SQLModel
    from src.models import User, Project, SharedProject
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# Test client fixture
@pytest_asyncio.fixture
async def client(app_with_db_dependency, setup_db) -> AsyncGenerator[AsyncClient, None]:
    app = app_with_db_dependency
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# We will use pytest-asyncio's event_loop fixture instead
# Don't define our own to avoid deprecation warning
