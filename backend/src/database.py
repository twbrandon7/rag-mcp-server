
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from src.config import settings

# Create async database engine
engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# Function to create all tables (only for testing/development)
async def create_db_and_tables():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(SQLModel.metadata.create_all)
