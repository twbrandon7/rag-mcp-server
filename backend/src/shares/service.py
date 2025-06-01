import secrets
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import SharedProject, Project, User
from src.projects.exceptions import ProjectNotFoundException
from src.shares.constants import SHARE_TOKEN_LENGTH
from src.shares.exceptions import (
    ShareNotFoundException,
    ShareTokenNotFoundException,
    ProjectAlreadySharedException,
    CannotShareWithSelfException,
    AccessDeniedException,
)


async def generate_unique_share_token(session: AsyncSession) -> str:
    """Generate a unique share token"""
    max_attempts = 10
    for _ in range(max_attempts):
        token = secrets.token_urlsafe(SHARE_TOKEN_LENGTH)
        # Check if token already exists
        result = await session.execute(
            select(SharedProject).where(SharedProject.share_token == token)
        )
        if not result.scalars().first():
            return token
    
    # If we couldn't generate a unique token after max_attempts, raise an error
    raise RuntimeError("Could not generate unique share token after multiple attempts")


async def create_public_share(
    session: AsyncSession, 
    project_id: UUID, 
    owner_user_id: UUID
) -> SharedProject:
    """Create a public share token for a project"""
    # Verify project exists and user owns it
    project_result = await session.execute(
        select(Project).where(
            and_(Project.project_id == project_id, Project.user_id == owner_user_id)
        )
    )
    project = project_result.scalars().first()
    if not project:
        raise ProjectNotFoundException("Project not found or access denied")
    
    # Check if public share already exists
    existing_share_result = await session.execute(
        select(SharedProject).where(
            and_(
                SharedProject.project_id == project_id,
                SharedProject.shared_with_user_id.is_(None)
            )
        )
    )
    existing_share = existing_share_result.scalars().first()
    if existing_share:
        raise ProjectAlreadySharedException("Project already has a public share token")
    
    # Generate unique token and create share
    share_token = await generate_unique_share_token(session)
    
    shared_project = SharedProject(
        project_id=project_id,
        shared_with_user_id=None,
        share_token=share_token
    )
    
    session.add(shared_project)
    await session.commit()
    await session.refresh(shared_project)
    
    return shared_project


async def share_with_user(
    session: AsyncSession,
    project_id: UUID,
    owner_user_id: UUID,
    shared_with_user_id: UUID
) -> SharedProject:
    """Share a project with a specific user"""
    # Verify project exists and user owns it
    project_result = await session.execute(
        select(Project).where(
            and_(Project.project_id == project_id, Project.user_id == owner_user_id)
        )
    )
    project = project_result.scalars().first()
    if not project:
        raise ProjectNotFoundException("Project not found or access denied")
    
    # Cannot share with self
    if owner_user_id == shared_with_user_id:
        raise CannotShareWithSelfException()
    
    # Verify target user exists
    user_result = await session.execute(
        select(User).where(User.user_id == shared_with_user_id)
    )
    target_user = user_result.scalars().first()
    if not target_user:
        raise ValueError("Target user not found")
    
    # Check if already shared with this user
    existing_share_result = await session.execute(
        select(SharedProject).where(
            and_(
                SharedProject.project_id == project_id,
                SharedProject.shared_with_user_id == shared_with_user_id
            )
        )
    )
    existing_share = existing_share_result.scalars().first()
    if existing_share:
        raise ProjectAlreadySharedException(f"Project already shared with user {shared_with_user_id}")
    
    shared_project = SharedProject(
        project_id=project_id,
        shared_with_user_id=shared_with_user_id,
        share_token=None
    )
    
    session.add(shared_project)
    await session.commit()
    await session.refresh(shared_project)
    
    return shared_project


async def get_project_shares(
    session: AsyncSession,
    project_id: UUID,
    owner_user_id: UUID
) -> List[SharedProject]:
    """Get all shares for a project"""
    # Verify project exists and user owns it
    project_result = await session.execute(
        select(Project).where(
            and_(Project.project_id == project_id, Project.user_id == owner_user_id)
        )
    )
    project = project_result.scalars().first()
    if not project:
        raise ProjectNotFoundException("Project not found or access denied")
    
    result = await session.execute(
        select(SharedProject).where(SharedProject.project_id == project_id)
    )
    
    return result.scalars().all()


async def get_shared_projects_for_user(
    session: AsyncSession,
    user_id: UUID
) -> List[dict]:
    """Get all projects shared with a user"""
    result = await session.execute(
        select(SharedProject, Project, User)
        .join(Project, SharedProject.project_id == Project.project_id)
        .join(User, Project.user_id == User.user_id)
        .where(SharedProject.shared_with_user_id == user_id)
        .options(selectinload(SharedProject.project))
    )
    
    shared_projects = []
    for shared_project, project, owner in result:
        shared_projects.append({
            "project_id": project.project_id,
            "project_name": project.project_name,
            "owner_email": owner.email,
            "shared_at": shared_project.created_at.isoformat()
        })
    
    return shared_projects


async def get_project_by_share_token(
    session: AsyncSession,
    share_token: str
) -> dict:
    """Get project information by share token"""
    result = await session.execute(
        select(SharedProject, Project, User)
        .join(Project, SharedProject.project_id == Project.project_id)
        .join(User, Project.user_id == User.user_id)
        .where(SharedProject.share_token == share_token)
    )
    
    row = result.first()
    if not row:
        raise ShareTokenNotFoundException("Share token not found")
    
    shared_project, project, owner = row
    
    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "owner_email": owner.email,
        "shared_at": shared_project.created_at.isoformat()
    }


async def revoke_share(
    session: AsyncSession,
    share_id: UUID,
    owner_user_id: UUID
) -> None:
    """Revoke a share"""
    # Get the share and verify ownership
    result = await session.execute(
        select(SharedProject, Project)
        .join(Project, SharedProject.project_id == Project.project_id)
        .where(
            and_(
                SharedProject.shared_project_id == share_id,
                Project.user_id == owner_user_id
            )
        )
    )
    
    row = result.first()
    if not row:
        raise ShareNotFoundException("Share not found or access denied")
    
    shared_project, _ = row
    
    await session.delete(shared_project)
    await session.commit()


async def can_user_access_project(
    session: AsyncSession,
    user_id: UUID,
    project_id: UUID
) -> bool:
    """Check if a user can access a project (owner or shared with)"""
    # Check if user owns the project
    owner_result = await session.execute(
        select(Project).where(
            and_(Project.project_id == project_id, Project.user_id == user_id)
        )
    )
    if owner_result.scalars().first():
        return True
    
    # Check if project is shared with user
    shared_result = await session.execute(
        select(SharedProject).where(
            and_(
                SharedProject.project_id == project_id,
                SharedProject.shared_with_user_id == user_id
            )
        )
    )
    if shared_result.scalars().first():
        return True
    
    return False
