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
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Create session
    async with async_test_session() as session:
        try:
            yield session
        finally:
            pass
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# Override get_db dependency to use test engine
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests."""
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
    from src.models import User, Project, SharedProject, URL, Chunk
    
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

# Test fixtures for users and projects
@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession):
    """Create a sample user for testing"""
    from src.models import User
    from src.auth.utils import get_password_hash
    
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_user_2(db_session: AsyncSession):
    """Create a second sample user for testing"""
    from src.models import User
    from src.auth.utils import get_password_hash
    
    user = User(
        email="test2@example.com",
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_project(db_session: AsyncSession, sample_user):
    """Create a sample project for testing"""
    from src.models import Project
    
    project = Project(
        project_name="Test Project",
        user_id=sample_user.user_id
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, sample_user):
    """Get auth headers for sample user"""
    response = await client.post("/api/v1/auth/token", data={
        "username": sample_user.email,
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_2(client: AsyncClient, sample_user_2):
    """Get auth headers for second sample user"""
    response = await client.post("/api/v1/auth/token", data={
        "username": sample_user_2.email,
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
