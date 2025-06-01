from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, get_db
from src.models import User
from src.users.schemas import UserCreate, UserResponse
from src.users.service import create_user
from src.shares.schemas import SharedProjectInfo
from src.shares.service import get_shared_projects_for_user

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
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


@router.get("/me/shared-projects", response_model=List[SharedProjectInfo])
async def list_shared_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> List[SharedProjectInfo]:
    """Get all projects shared with the current user"""
    shared_projects = await get_shared_projects_for_user(session, current_user.user_id)
    return [
        SharedProjectInfo(
            project_id=project["project_id"],
            project_name=project["project_name"],
            owner_email=project["owner_email"],
            shared_at=project["shared_at"]
        )
        for project in shared_projects
    ]
