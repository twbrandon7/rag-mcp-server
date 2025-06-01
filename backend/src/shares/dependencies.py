from uuid import UUID
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, get_db
from src.models import User
from src.shares.service import can_user_access_project
from src.shares.exceptions import AccessDeniedException


async def verify_project_access(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UUID:
    """Verify that the current user has access to the project"""
    has_access = await can_user_access_project(session, current_user.user_id, project_id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project"
        )
    return project_id
