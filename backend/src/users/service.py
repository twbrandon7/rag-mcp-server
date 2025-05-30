
from sqlmodel import Session, select

from src.auth.exceptions import EmailExistsException
from src.auth.utils import get_password_hash
from src.models import User
from src.users.schemas import UserCreate


async def create_user(session: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.exec(statement)
    existing_user = result.first()
    
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


async def get_user_by_id(session: Session, user_id: str) -> User:
    """Get user by ID."""
    statement = select(User).where(User.user_id == user_id)
    result = await session.exec(statement)
    return result.first()
