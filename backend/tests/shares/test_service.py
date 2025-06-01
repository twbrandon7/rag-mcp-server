import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Project, SharedProject
from src.shares.service import (
    create_public_share,
    share_with_user,
    get_project_shares,
    get_shared_projects_for_user,
    get_project_by_share_token,
    revoke_share,
    can_user_access_project,
)
from src.shares.exceptions import (
    ShareNotFoundException,
    ShareTokenNotFoundException,
    ProjectAlreadySharedException,
    CannotShareWithSelfException,
)
from src.projects.exceptions import ProjectNotFoundException


@pytest.mark.asyncio
async def test_create_public_share_success(db_session: AsyncSession, sample_user: User, sample_project: Project):
    """Test creating a public share token successfully"""
    shared_project = await create_public_share(db_session, sample_project.project_id, sample_user.user_id)
    
    assert shared_project.project_id == sample_project.project_id
    assert shared_project.shared_with_user_id is None
    assert shared_project.share_token is not None
    assert len(shared_project.share_token) > 10  # Token should be reasonably long


@pytest.mark.asyncio
async def test_create_public_share_project_not_found(db_session: AsyncSession, sample_user: User):
    """Test creating public share for non-existent project"""
    non_existent_project_id = uuid4()
    
    with pytest.raises(ProjectNotFoundException):
        await create_public_share(db_session, non_existent_project_id, sample_user.user_id)


@pytest.mark.asyncio
async def test_create_public_share_access_denied(db_session: AsyncSession, sample_project: Project):
    """Test creating public share when user doesn't own the project"""
    other_user_id = uuid4()
    
    with pytest.raises(ProjectNotFoundException):
        await create_public_share(db_session, sample_project.project_id, other_user_id)


@pytest.mark.asyncio
async def test_create_public_share_already_exists(db_session: AsyncSession, sample_user: User, sample_project: Project):
    """Test creating public share when one already exists"""
    # Create first share
    await create_public_share(db_session, sample_project.project_id, sample_user.user_id)
    
    # Try to create another
    with pytest.raises(ProjectAlreadySharedException):
        await create_public_share(db_session, sample_project.project_id, sample_user.user_id)


@pytest.mark.asyncio
async def test_share_with_user_success(db_session: AsyncSession, sample_user: User, sample_project: Project, sample_user_2: User):
    """Test sharing project with another user successfully"""
    shared_project = await share_with_user(
        db_session, 
        sample_project.project_id, 
        sample_user.user_id, 
        sample_user_2.user_id
    )
    
    assert shared_project.project_id == sample_project.project_id
    assert shared_project.shared_with_user_id == sample_user_2.user_id
    assert shared_project.share_token is None


@pytest.mark.asyncio
async def test_share_with_user_cannot_share_with_self(db_session: AsyncSession, sample_user: User, sample_project: Project):
    """Test that user cannot share project with themselves"""
    with pytest.raises(CannotShareWithSelfException):
        await share_with_user(
            db_session, 
            sample_project.project_id, 
            sample_user.user_id, 
            sample_user.user_id
        )


@pytest.mark.asyncio
async def test_share_with_user_target_user_not_found(db_session: AsyncSession, sample_user: User, sample_project: Project):
    """Test sharing with non-existent user"""
    non_existent_user_id = uuid4()
    
    with pytest.raises(ValueError, match="Target user not found"):
        await share_with_user(
            db_session, 
            sample_project.project_id, 
            sample_user.user_id, 
            non_existent_user_id
        )


@pytest.mark.asyncio
async def test_share_with_user_already_shared(db_session: AsyncSession, sample_user: User, sample_project: Project, sample_user_2: User):
    """Test sharing with user when already shared"""
    # Share first time
    await share_with_user(
        db_session, 
        sample_project.project_id, 
        sample_user.user_id, 
        sample_user_2.user_id
    )
    
    # Try to share again
    with pytest.raises(ProjectAlreadySharedException):
        await share_with_user(
            db_session, 
            sample_project.project_id, 
            sample_user.user_id, 
            sample_user_2.user_id
        )


@pytest.mark.asyncio
async def test_get_project_shares(db_session: AsyncSession, sample_user: User, sample_project: Project, sample_user_2: User):
    """Test getting all shares for a project"""
    # Create public share and user share
    await create_public_share(db_session, sample_project.project_id, sample_user.user_id)
    await share_with_user(
        db_session, 
        sample_project.project_id, 
        sample_user.user_id, 
        sample_user_2.user_id
    )
    
    shares = await get_project_shares(db_session, sample_project.project_id, sample_user.user_id)
    
    assert len(shares) == 2
    public_share = next((s for s in shares if s.share_token is not None), None)
    user_share = next((s for s in shares if s.shared_with_user_id is not None), None)
    
    assert public_share is not None
    assert user_share is not None
    assert user_share.shared_with_user_id == sample_user_2.user_id


@pytest.mark.asyncio
async def test_get_shared_projects_for_user(db_session: AsyncSession, sample_user: User, sample_project: Project, sample_user_2: User):
    """Test getting projects shared with a user"""
    # Share project with user_2
    await share_with_user(
        db_session, 
        sample_project.project_id, 
        sample_user.user_id, 
        sample_user_2.user_id
    )
    
    shared_projects = await get_shared_projects_for_user(db_session, sample_user_2.user_id)
    
    assert len(shared_projects) == 1
    assert shared_projects[0]["project_id"] == sample_project.project_id
    assert shared_projects[0]["project_name"] == sample_project.project_name
    assert shared_projects[0]["owner_email"] == sample_user.email


@pytest.mark.asyncio
async def test_get_project_by_share_token(db_session: AsyncSession, sample_user: User, sample_project: Project):
    """Test getting project by share token"""
    shared_project = await create_public_share(db_session, sample_project.project_id, sample_user.user_id)
    
    project_info = await get_project_by_share_token(db_session, shared_project.share_token)
    
    assert project_info["project_id"] == sample_project.project_id
    assert project_info["project_name"] == sample_project.project_name
    assert project_info["owner_email"] == sample_user.email


@pytest.mark.asyncio
async def test_get_project_by_invalid_share_token(db_session: AsyncSession):
    """Test getting project with invalid share token"""
    with pytest.raises(ShareTokenNotFoundException):
        await get_project_by_share_token(db_session, "invalid-token")


@pytest.mark.asyncio
async def test_revoke_share(db_session: AsyncSession, sample_user: User, sample_project: Project, sample_user_2: User):
    """Test revoking a share"""
    shared_project = await share_with_user(
        db_session, 
        sample_project.project_id, 
        sample_user.user_id, 
        sample_user_2.user_id
    )
    
    # Revoke the share
    await revoke_share(db_session, shared_project.shared_project_id, sample_user.user_id)
    
    # Verify share is gone
    shares = await get_project_shares(db_session, sample_project.project_id, sample_user.user_id)
    assert len(shares) == 0


@pytest.mark.asyncio
async def test_revoke_share_not_found(db_session: AsyncSession, sample_user: User):
    """Test revoking non-existent share"""
    non_existent_share_id = uuid4()
    
    with pytest.raises(ShareNotFoundException):
        await revoke_share(db_session, non_existent_share_id, sample_user.user_id)


@pytest.mark.asyncio
async def test_can_user_access_project_owner(db_session: AsyncSession, sample_user: User, sample_project: Project):
    """Test that project owner can access project"""
    has_access = await can_user_access_project(db_session, sample_user.user_id, sample_project.project_id)
    assert has_access is True


@pytest.mark.asyncio
async def test_can_user_access_project_shared_user(db_session: AsyncSession, sample_user: User, sample_project: Project, sample_user_2: User):
    """Test that user with shared access can access project"""
    # Share project
    await share_with_user(
        db_session, 
        sample_project.project_id, 
        sample_user.user_id, 
        sample_user_2.user_id
    )
    
    has_access = await can_user_access_project(db_session, sample_user_2.user_id, sample_project.project_id)
    assert has_access is True


@pytest.mark.asyncio
async def test_can_user_access_project_no_access(db_session: AsyncSession, sample_project: Project, sample_user_2: User):
    """Test that user without access cannot access project"""
    has_access = await can_user_access_project(db_session, sample_user_2.user_id, sample_project.project_id)
    assert has_access is False
