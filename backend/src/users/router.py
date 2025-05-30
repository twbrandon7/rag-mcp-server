
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from src.auth.dependencies import get_current_user, get_db
from src.models import User
from src.users.schemas import UserCreate, UserResponse
from src.users.service import create_user

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    session: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Register a new user."""
    user = await create_user(session, user_data)
    return UserResponse(
        user_id=user.user_id,
        created_at=user.created_at
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    """Get information about the currently authenticated user."""
    return UserResponse(
        user_id=current_user.user_id,
        created_at=current_user.created_at
    )
