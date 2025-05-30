
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import EmailExistsException
from src.auth.utils import get_password_hash
from src.models import User
from src.users.schemas import UserCreate


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise EmailExistsException()
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    
    # Save to database
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    return db_user


async def get_user_by_id(session: AsyncSession, user_id: str) -> User:
    """Get user by ID."""
    statement = select(User).where(User.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().first()
