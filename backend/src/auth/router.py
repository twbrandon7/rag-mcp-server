
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, get_db
from src.auth.exceptions import InvalidCredentialsException
from src.auth.schemas import Token, LoginCredentials, OAuthRequest
from src.auth.service import authenticate_user, create_user_token, validate_oauth_token
from src.models import User

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """Login with email and password to get access token."""
    credentials = LoginCredentials(
        email=form_data.username,  # OAuth2 form uses 'username' for email
        password=form_data.password
    )
    
    # Authenticate user
    user = await authenticate_user(session, credentials)
    if not user:
        raise InvalidCredentialsException()
    
    # Create and return access token
    return await create_user_token(user)


@router.post("/google", response_model=Token)
async def login_with_google(
    oauth_data: OAuthRequest,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """Login with Google OAuth token."""
    # In a real implementation, you'd validate the token with Google's API
    # For simplicity, we're assuming the token is a valid Google token with user info
    # Normally you would do something like:
    # google_user_info = await google_client.validate_token(oauth_data.token)
    
    # Mock implementation - in real code, replace with actual Google validation
    google_user_info = {
        "id": "google_123456789",
        "email": "user@example.com"
    }
    
    # Validate or create user
    user = await validate_oauth_token(
        session,
        "google",
        oauth_data.token,
        google_user_info["email"],
        google_user_info["id"]
    )
    
    # Create and return access token
    return await create_user_token(user)


@router.post("/microsoft", response_model=Token)
async def login_with_microsoft(
    oauth_data: OAuthRequest,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """Login with Microsoft OAuth token."""
    # In a real implementation, you'd validate the token with Microsoft's API
    # For simplicity, we're assuming the token is valid with user info
    # Normally you would do something like:
    # ms_user_info = await microsoft_client.validate_token(oauth_data.token)
    
    # Mock implementation - in real code, replace with actual Microsoft validation
    ms_user_info = {
        "id": "microsoft_123456789",
        "email": "user@example.com"
    }
    
    # Validate or create user
    user = await validate_oauth_token(
        session,
        "microsoft",
        oauth_data.token,
        ms_user_info["email"],
        ms_user_info["id"]
    )
    
    # Create and return access token
    return await create_user_token(user)
