import pytest
from unittest.mock import AsyncMock, patch, Mock
from uuid import uuid4

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


# Mock objects for testing
@pytest.fixture
def mock_user():
    user = Mock()
    user.user_id = uuid4()
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_user_2():
    user = Mock()
    user.user_id = uuid4()
    user.email = "test2@example.com"
    return user


@pytest.fixture
def mock_project(mock_user):
    project = Mock()
    project.project_id = uuid4()
    project.project_name = "Test Project"
    project.user_id = mock_user.user_id
    return project


@pytest.mark.asyncio
@patch('src.shares.service.select')
@patch('src.shares.service.generate_unique_share_token')
async def test_create_public_share_success(
    mock_generate_token,
    mock_select,
    mock_user,
    mock_project
):
    """Test creating a public share token successfully"""
    mock_session = AsyncMock()
    mock_generate_token.return_value = "test-token-123"

    # Mock project exists query - result should be regular Mock, scalars() returns Mock with first() method
    mock_project_result = Mock()
    mock_project_scalars = Mock()
    mock_project_scalars.first.return_value = mock_project
    mock_project_result.scalars.return_value = mock_project_scalars

    # Mock existing share query (no existing share)
    mock_share_result = Mock()
    mock_share_scalars = Mock()
    mock_share_scalars.first.return_value = None
    mock_share_result.scalars.return_value = mock_share_scalars

    mock_session.execute.side_effect = [mock_project_result, mock_share_result]

    result = await create_public_share(mock_session, mock_project.project_id, mock_user.user_id)

    assert result.project_id == mock_project.project_id
    assert result.shared_with_user_id is None
    assert result.share_token == "test-token-123"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_create_public_share_project_not_found(mock_select, mock_user):
    """Test creating public share for non-existent project"""
    mock_session = AsyncMock()

    # Mock project not found
    mock_result = Mock()
    mock_scalars = Mock()
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    with pytest.raises(ProjectNotFoundException):
        await create_public_share(mock_session, uuid4(), mock_user.user_id)


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_share_with_user_success(mock_select, mock_user, mock_user_2, mock_project):
    """Test sharing a project with a specific user successfully"""
    mock_session = AsyncMock()

    # Mock project exists
    mock_project_result = Mock()
    mock_project_scalars = Mock()
    mock_project_scalars.first.return_value = mock_project
    mock_project_result.scalars.return_value = mock_project_scalars

    # Mock target user exists
    mock_user_result = Mock()
    mock_user_scalars = Mock()
    mock_user_scalars.first.return_value = mock_user_2
    mock_user_result.scalars.return_value = mock_user_scalars

    # Mock no existing share
    mock_share_result = Mock()
    mock_share_scalars = Mock()
    mock_share_scalars.first.return_value = None
    mock_share_result.scalars.return_value = mock_share_scalars

    mock_session.execute.side_effect = [mock_project_result, mock_user_result, mock_share_result]

    result = await share_with_user(
        mock_session,
        mock_project.project_id,
        mock_user.user_id,
        mock_user_2.user_id
    )

    assert result.project_id == mock_project.project_id
    assert result.shared_with_user_id == mock_user_2.user_id
    assert result.share_token is None
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_share_with_user_cannot_share_with_self(mock_select, mock_user, mock_project):
    """Test that user cannot share project with themselves"""
    mock_session = AsyncMock()

    # Mock project exists
    mock_result = Mock()
    mock_scalars = Mock()
    mock_scalars.first.return_value = mock_project
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    with pytest.raises(CannotShareWithSelfException):
        await share_with_user(
            mock_session,
            mock_project.project_id,
            mock_user.user_id,
            mock_user.user_id  # Same user
        )


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_get_project_shares_success(mock_select, mock_user, mock_project):
    """Test getting project shares successfully"""
    mock_session = AsyncMock()

    # Mock project exists
    mock_project_result = Mock()
    mock_project_scalars = Mock()
    mock_project_scalars.first.return_value = mock_project
    mock_project_result.scalars.return_value = mock_project_scalars

    # Mock shares exist
    mock_shares_result = Mock()
    mock_shares_scalars = Mock()
    mock_shares_scalars.all.return_value = []
    mock_shares_result.scalars.return_value = mock_shares_scalars

    mock_session.execute.side_effect = [mock_project_result, mock_shares_result]

    result = await get_project_shares(mock_session, mock_project.project_id, mock_user.user_id)

    assert isinstance(result, list)


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_get_shared_projects_for_user(mock_select, mock_user_2):
    """Test getting projects shared with a user"""
    mock_session = AsyncMock()

    # Mock query result - this function iterates over the result directly
    mock_result = []  # Just use an empty list since it's iterable
    mock_session.execute.return_value = mock_result

    result = await get_shared_projects_for_user(mock_session, mock_user_2.user_id)

    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_get_project_by_share_token_success(mock_select, mock_project):
    """Test getting project by share token successfully"""
    mock_session = AsyncMock()

    # Mock successful result
    mock_result = Mock()
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_shared_project = Mock()
    mock_shared_project.created_at.isoformat.return_value = "2024-01-01T00:00:00"

    mock_result.first.return_value = (mock_shared_project, mock_project, mock_user)
    mock_session.execute.return_value = mock_result

    result = await get_project_by_share_token(mock_session, "test-token")

    assert result["project_id"] == mock_project.project_id
    assert result["project_name"] == mock_project.project_name
    assert result["owner_email"] == "test@example.com"


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_get_project_by_share_token_not_found(mock_select):
    """Test getting project by invalid share token"""
    mock_session = AsyncMock()

    # Mock no result
    mock_result = Mock()
    mock_result.first.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(ShareTokenNotFoundException):
        await get_project_by_share_token(mock_session, "invalid-token")


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_revoke_share_success(mock_select, mock_user):
    """Test revoking a share successfully"""
    mock_session = AsyncMock()

    # Mock successful result
    mock_result = Mock()
    mock_shared_project = Mock()
    mock_project = Mock()
    mock_result.first.return_value = (mock_shared_project, mock_project)
    mock_session.execute.return_value = mock_result

    # Should not raise exception
    await revoke_share(mock_session, uuid4(), mock_user.user_id)

    # Verify delete was called
    mock_session.delete.assert_called_once_with(mock_shared_project)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_revoke_share_not_found(mock_select, mock_user):
    """Test revoking non-existent share"""
    mock_session = AsyncMock()

    # Mock no result
    mock_result = Mock()
    mock_result.first.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(ShareNotFoundException):
        await revoke_share(mock_session, uuid4(), mock_user.user_id)


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_can_user_access_project_owner(mock_select, mock_user, mock_project):
    """Test that project owner can access project"""
    mock_session = AsyncMock()

    # Mock owner result
    mock_owner_result = Mock()
    mock_owner_scalars = Mock()
    mock_owner_scalars.first.return_value = mock_project
    mock_owner_result.scalars.return_value = mock_owner_scalars
    mock_session.execute.return_value = mock_owner_result

    result = await can_user_access_project(mock_session, mock_user.user_id, mock_project.project_id)

    assert result is True


@pytest.mark.asyncio
@patch('src.shares.service.select')
async def test_can_user_access_project_no_access(mock_select, mock_user_2, mock_project):
    """Test that user without access cannot access project"""
    mock_session = AsyncMock()

    # Mock no access for both owner and share checks
    mock_result = Mock()
    mock_scalars = Mock()
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    result = await can_user_access_project(mock_session, mock_user_2.user_id, mock_project.project_id)

    assert result is False
