
from datetime import timedelta
from typing import Optional

from sqlmodel import Session, select
from passlib.context import CryptContext

from src.auth.constants import ErrorCode
from src.auth.exceptions import EmailExistsException, InvalidCredentialsException
from src.auth.schemas import Token, LoginCredentials
from src.auth.utils import verify_password, create_access_token
from src.models import User, UserCreate


async def authenticate_user(
    session: Session, credentials: LoginCredentials
) -> Optional[User]:
    """Authenticate a user with email and password."""
    # Find the user by email
    statement = select(User).where(User.email == credentials.email)
    result = await session.exec(statement)
    user = result.first()
    
    # Check if user exists and password is correct
    if not user or not user.password_hash:
        raise InvalidCredentialsException()
    
    if not verify_password(credentials.password, user.password_hash):
        raise InvalidCredentialsException()
    
    return user


async def create_user_token(user: User) -> Token:
    """Create an access token for the user."""
    access_token_expires = timedelta(minutes=60 * 24 * 8)  # 8 days
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


async def validate_oauth_token(
    session: Session, 
    oauth_provider: str, 
    token: str, 
    email: str,
    provider_user_id: str
) -> User:
    """
    Validate OAuth token and return or create user.
    
    Args:
        session: Database session
        oauth_provider: Provider name ('google' or 'microsoft')
        token: OAuth token
        email: User email from OAuth provider
        provider_user_id: User ID from OAuth provider
    """
    # Check if user with this email already exists
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    user = result.first()
    
    if user:
        # Update the user with provider ID if needed
        if oauth_provider == "google" and not user.google_id:
            user.google_id = provider_user_id
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif oauth_provider == "microsoft" and not user.microsoft_id:
            user.microsoft_id = provider_user_id
            session.add(user)
            await session.commit()
            await session.refresh(user)
    else:
        # Create new user with OAuth data
        new_user = User(email=email)
        if oauth_provider == "google":
            new_user.google_id = provider_user_id
        elif oauth_provider == "microsoft":
            new_user.microsoft_id = provider_user_id
            
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        user = new_user
        
    return user
