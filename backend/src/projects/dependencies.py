from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.auth.dependencies import get_current_user, get_db
from src.models import Project, User
from src.projects.service import get_project

# Common dependencies for project endpoints
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_project_by_id(
    project_id: UUID,
    current_user: CurrentUser,
    session: DbSession
) -> Project:
    """Dependency to get a project by ID or raise 404."""
    return await get_project(session, current_user.user_id, project_id)
