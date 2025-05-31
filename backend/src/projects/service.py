from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import List, Optional

from src.models import Project, User
from src.projects.exceptions import (
    ProjectNotFoundException, 
    DuplicateProjectNameException
)
from src.projects.schemas import ProjectCreate, ProjectUpdate


async def create_project(
    session: AsyncSession,
    user: User,
    project_data: ProjectCreate
) -> Project:
    """Create a new project for the user."""
    project = Project(
        project_name=project_data.project_name,
        user_id=user.user_id
    )
    session.add(project)
    try:
        await session.commit()
        await session.refresh(project)
        return project
    except IntegrityError:
        await session.rollback()
        # This is likely a duplicate project name for the same user
        raise DuplicateProjectNameException(project_data.project_name)


async def get_project(
    session: AsyncSession,
    user_id: UUID,
    project_id: UUID
) -> Project:
    """Get a project by ID, ensuring it belongs to the user."""
    statement = select(Project).where(
        Project.project_id == project_id,
        Project.user_id == user_id
    )
    result = await session.execute(statement)
    project = result.scalars().first()
    if not project:
        raise ProjectNotFoundException(str(project_id))
    return project


async def get_user_projects(
    session: AsyncSession,
    user_id: UUID
) -> List[Project]:
    """Get all projects belonging to a user."""
    statement = select(Project).where(Project.user_id == user_id)
    result = await session.execute(statement)
    projects = result.scalars().all()
    return list(projects)


async def update_project(
    session: AsyncSession,
    project: Project,
    project_data: ProjectUpdate
) -> Project:
    """Update an existing project."""
    project.project_name = project_data.project_name
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def delete_project(
    session: AsyncSession,
    project: Project
) -> None:
    """Delete a project."""
    await session.delete(project)
    await session.commit()
