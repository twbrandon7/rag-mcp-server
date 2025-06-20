
from typing import Annotated, AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidTokenException, UserNotFoundException
from src.auth.schemas import TokenData
from src.auth.utils import decode_access_token
from src.database import engine
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            pass  # AsyncSession automatically closes in the async context manager


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Get the current user from JWT token."""
    # Decode the JWT token
    payload = decode_access_token(token)
    
    # Extract user ID from token
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()
    
    # Query the user from the database
    try:
        uuid_obj = UUID(user_id)
    except ValueError:
        raise InvalidTokenException()
    
    statement = select(User).where(User.user_id == uuid_obj)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if not user:
        raise UserNotFoundException()
    
    return user


async def get_optional_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get the current user, or None if not authenticated."""
    try:
        return await get_current_user(token, session)
    except HTTPException:
        return None
