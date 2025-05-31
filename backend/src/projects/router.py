from typing import List, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, get_db
from src.models import User, Project
from src.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from src.projects.service import (
    create_project,
    get_project,
    get_user_projects,
    update_project,
    delete_project,
)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_new_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectResponse:
    """Create a new project for organizing URLs and vectors."""
    project = await create_project(session, current_user, project_data)
    return ProjectResponse(
        project_id=project.project_id,
        user_id=project.user_id,
        project_name=project.project_name,
        created_at=project.created_at
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> List[ProjectResponse]:
    """Get all projects belonging to the authenticated user."""
    projects = await get_user_projects(session, current_user.user_id)
    return [
        ProjectResponse(
            project_id=project.project_id,
            user_id=project.user_id,
            project_name=project.project_name,
            created_at=project.created_at
        )
        for project in projects
    ]


async def get_project_or_404(
    project_id: UUID,
    current_user: User,
    session: AsyncSession,
) -> Project:
    """Get a project or raise 404 if not found."""
    # The get_project function will now raise ProjectNotFoundException if not found
    return await get_project(session, current_user.user_id, project_id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectResponse:
    """Get details of a specific project."""
    project = await get_project_or_404(project_id, current_user, session)
    return ProjectResponse(
        project_id=project.project_id,
        user_id=project.user_id,
        project_name=project.project_name,
        created_at=project.created_at
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project_by_id(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectResponse:
    """Update a project's details."""
    project = await get_project_or_404(project_id, current_user, session)
    updated_project = await update_project(session, project, project_data)
    return ProjectResponse(
        project_id=updated_project.project_id,
        user_id=updated_project.user_id,
        project_name=updated_project.project_name,
        created_at=updated_project.created_at
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_id(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    """Delete a project and all its associated data."""
    project = await get_project_or_404(project_id, current_user, session)
    await delete_project(session, project)
