from typing import List, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, get_db
from src.models import User
from src.shares.schemas import (
    ShareTokenCreate,
    ShareWithUserCreate,
    ShareResponse,
    PublicShareResponse,
    SharedProjectInfo,
)
from src.shares.service import (
    create_public_share,
    share_with_user,
    get_project_shares,
    get_shared_projects_for_user,
    get_project_by_share_token,
    revoke_share,
)
from src.shares.exceptions import (
    ShareNotFoundException,
    ShareTokenNotFoundException,
    ProjectAlreadySharedException,
    CannotShareWithSelfException,
)
from src.projects.exceptions import ProjectNotFoundException


router = APIRouter()


@router.post("/{project_id}/shares/public", status_code=status.HTTP_201_CREATED, response_model=PublicShareResponse)
async def create_public_share_token(
    project_id: UUID,
    share_data: ShareTokenCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> PublicShareResponse:
    """Create a public share token for a project"""
    try:
        shared_project = await create_public_share(session, project_id, current_user.user_id)
        created_at = shared_project.created_at
        if hasattr(created_at, 'isoformat'):
            created_at_str = created_at.isoformat()
        else:
            created_at_str = str(created_at)
        
        return PublicShareResponse(
            share_id=shared_project.shared_project_id,
            project_id=shared_project.project_id,
            share_token=shared_project.share_token,
            created_at=created_at_str
        )
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    except ProjectAlreadySharedException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project already has a public share token"
        )


@router.post("/{project_id}/shares/users", status_code=status.HTTP_201_CREATED, response_model=ShareResponse)
async def share_project_with_user(
    project_id: UUID,
    share_data: ShareWithUserCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ShareResponse:
    """Share a project with a specific user"""
    try:
        shared_project = await share_with_user(
            session, 
            project_id, 
            current_user.user_id, 
            share_data.shared_with_user_id
        )
        created_at = shared_project.created_at
        if hasattr(created_at, 'isoformat'):
            created_at_str = created_at.isoformat()
        else:
            created_at_str = str(created_at)
        
        return ShareResponse(
            share_id=shared_project.shared_project_id,
            project_id=shared_project.project_id,
            shared_with_user_id=shared_project.shared_with_user_id,
            share_token=shared_project.share_token,
            created_at=created_at_str
        )
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    except CannotShareWithSelfException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share project with yourself"
        )
    except ProjectAlreadySharedException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project already shared with this user"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )


@router.get("/{project_id}/shares", response_model=List[ShareResponse])
async def list_project_shares(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> List[ShareResponse]:
    """Get all shares for a project"""
    try:
        shares = await get_project_shares(session, project_id, current_user.user_id)
        share_responses = []
        for share in shares:
            created_at = share.created_at
            if hasattr(created_at, 'isoformat'):
                created_at_str = created_at.isoformat()
            else:
                created_at_str = str(created_at)
            
            share_responses.append(ShareResponse(
                share_id=share.shared_project_id,
                project_id=share.project_id,
                shared_with_user_id=share.shared_with_user_id,
                share_token=share.share_token,
                created_at=created_at_str
            ))
        return share_responses
    except ProjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )





@router.get("/public/{share_token}", response_model=SharedProjectInfo)
async def get_project_by_public_token(
    share_token: str,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> SharedProjectInfo:
    """Get project information using a public share token (no authentication required)"""
    try:
        project_info = await get_project_by_share_token(session, share_token)
        return SharedProjectInfo(
            project_id=project_info["project_id"],
            project_name=project_info["project_name"],
            owner_email=project_info["owner_email"],
            shared_at=project_info["shared_at"]
        )
    except ShareTokenNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share token not found"
        )


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_project_share(
    share_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    """Revoke a project share"""
    try:
        await revoke_share(session, share_id, current_user.user_id)
    except ShareNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
