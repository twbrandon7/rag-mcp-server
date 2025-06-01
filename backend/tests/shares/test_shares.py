import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.models import User, Project, SharedProject


@pytest.mark.asyncio
@patch('src.shares.router.create_public_share')
async def test_create_public_share_token(
    mock_create_public_share: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project
):
    """Test creating a public share token for a project"""
    # Mock the service response
    mock_shared_project = SharedProject(
        shared_project_id=uuid4(),
        project_id=sample_project.project_id,
        shared_with_user_id=None,
        share_token="test-token-123",
        created_at="2024-01-01T00:00:00"
    )
    mock_create_public_share.return_value = mock_shared_project
    
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        json={},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "share_id" in data
    assert "project_id" in data
    assert "share_token" in data
    assert "created_at" in data
    assert data["project_id"] == str(sample_project.project_id)
    assert data["share_token"] == "test-token-123"


@pytest.mark.asyncio
@patch('src.shares.router.create_public_share')
async def test_create_public_share_token_already_exists(
    mock_create_public_share: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project
):
    """Test creating a public share token when one already exists"""
    from src.shares.exceptions import ProjectAlreadySharedException
    
    # Mock the service to raise exception
    mock_create_public_share.side_effect = ProjectAlreadySharedException()
    
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        json={},
        headers=auth_headers
    )
    
    assert response.status_code == 409
    assert "already has a public share token" in response.json()["detail"]


@pytest.mark.asyncio
@patch('src.shares.router.create_public_share')
async def test_create_public_share_token_project_not_found(
    mock_create_public_share: AsyncMock,
    client: AsyncClient,
    auth_headers: dict
):
    """Test creating a public share token for non-existent project"""
    from src.projects.exceptions import ProjectNotFoundException
    
    # Mock the service to raise exception
    mock_create_public_share.side_effect = ProjectNotFoundException(project_id="test-id")
    
    fake_project_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.post(
        f"/api/v1/projects/{fake_project_id}/shares/public",
        json={},
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
@patch('src.shares.router.share_with_user')
async def test_share_project_with_user(
    mock_share_with_user: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project,
    sample_user_2: User
):
    """Test sharing a project with a specific user"""
    # Mock the service response
    mock_shared_project = SharedProject(
        shared_project_id=uuid4(),
        project_id=sample_project.project_id,
        shared_with_user_id=sample_user_2.user_id,
        share_token=None,
        created_at="2024-01-01T00:00:00"
    )
    mock_share_with_user.return_value = mock_shared_project
    
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        json={"shared_with_user_id": str(sample_user_2.user_id)},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "share_id" in data
    assert "project_id" in data
    assert "shared_with_user_id" in data
    assert "created_at" in data
    assert data["project_id"] == str(sample_project.project_id)
    assert data["shared_with_user_id"] == str(sample_user_2.user_id)
    assert data["share_token"] is None


@pytest.mark.asyncio
@patch('src.shares.router.share_with_user')
async def test_share_project_with_self(
    mock_share_with_user: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project,
    sample_user: User
):
    """Test sharing a project with yourself (should fail)"""
    from src.shares.exceptions import CannotShareWithSelfException
    
    # Mock the service to raise exception
    mock_share_with_user.side_effect = CannotShareWithSelfException()
    
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        json={"shared_with_user_id": str(sample_user.user_id)},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "Cannot share project with yourself" in response.json()["detail"]


@pytest.mark.asyncio
@patch('src.shares.router.share_with_user')
async def test_share_project_with_user_already_shared(
    mock_share_with_user: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project,
    sample_user_2: User
):
    """Test sharing a project with a user when already shared"""
    from src.shares.exceptions import ProjectAlreadySharedException
    
    # Mock the service to raise exception
    mock_share_with_user.side_effect = ProjectAlreadySharedException()
    
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        json={"shared_with_user_id": str(sample_user_2.user_id)},
        headers=auth_headers
    )
    
    assert response.status_code == 409
    assert "already shared with this user" in response.json()["detail"]


@pytest.mark.asyncio
@patch('src.shares.router.share_with_user')
async def test_share_project_with_nonexistent_user(
    mock_share_with_user: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project
):
    """Test sharing a project with a non-existent user"""
    # Mock the service to raise ValueError
    mock_share_with_user.side_effect = ValueError("Target user not found")
    
    fake_user_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        json={"shared_with_user_id": fake_user_id},
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "Target user not found" in response.json()["detail"]


@pytest.mark.asyncio
@patch('src.shares.router.get_project_shares')
async def test_list_project_shares(
    mock_get_project_shares: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project,
    sample_user_2: User
):
    """Test listing all shares for a project"""
    # Mock both types of shares
    public_share = SharedProject(
        shared_project_id=uuid4(),
        project_id=sample_project.project_id,
        shared_with_user_id=None,
        share_token="test-token-123",
        created_at="2024-01-01T00:00:00"
    )
    user_share = SharedProject(
        shared_project_id=uuid4(),
        project_id=sample_project.project_id,
        shared_with_user_id=sample_user_2.user_id,
        share_token=None,
        created_at="2024-01-01T00:00:00"
    )
    mock_get_project_shares.return_value = [public_share, user_share]
    
    response = await client.get(
        f"/api/v1/projects/{sample_project.project_id}/shares",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Check that we have both types of shares
    public_share_data = next((s for s in data if s["share_token"] is not None), None)
    user_share_data = next((s for s in data if s["shared_with_user_id"] is not None), None)
    
    assert public_share_data is not None
    assert user_share_data is not None
    assert user_share_data["shared_with_user_id"] == str(sample_user_2.user_id)


@pytest.mark.asyncio
@patch('src.shares.router.get_project_shares')
async def test_list_project_shares_empty(
    mock_get_project_shares: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project
):
    """Test listing shares for a project with no shares"""
    mock_get_project_shares.return_value = []
    
    response = await client.get(
        f"/api/v1/projects/{sample_project.project_id}/shares",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
@patch('src.users.router.get_shared_projects_for_user')
async def test_list_shared_projects(
    mock_get_shared_projects_for_user: AsyncMock,
    client: AsyncClient,
    auth_headers_2: dict,
    sample_project: Project,
    sample_user_2: User
):
    """Test listing projects shared with current user"""
    # Mock the service response
    mock_shared_projects = [{
        "project_id": sample_project.project_id,
        "project_name": sample_project.project_name,
        "owner_email": "test@example.com",
        "shared_at": "2024-01-01T00:00:00"
    }]
    mock_get_shared_projects_for_user.return_value = mock_shared_projects

    response = await client.get(
        "/api/v1/users/me/shared-projects",
        headers=auth_headers_2
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["project_id"] == str(sample_project.project_id)
    assert data[0]["project_name"] == sample_project.project_name
    assert "owner_email" in data[0]
    assert "shared_at" in data[0]


@pytest.mark.asyncio
@patch('src.shares.router.get_project_by_share_token')
async def test_get_project_by_public_token(
    mock_get_project_by_share_token: AsyncMock,
    client: AsyncClient,
    sample_project: Project
):
    """Test accessing project info via public share token"""
    # Mock the service response
    mock_project_info = {
        "project_id": sample_project.project_id,
        "project_name": sample_project.project_name,
        "owner_email": "test@example.com",
        "shared_at": "2024-01-01T00:00:00"
    }
    mock_get_project_by_share_token.return_value = mock_project_info
    
    response = await client.get("/api/v1/projects/public/test-token-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == str(sample_project.project_id)
    assert data["project_name"] == sample_project.project_name
    assert "owner_email" in data
    assert "shared_at" in data


@pytest.mark.asyncio
@patch('src.shares.router.get_project_by_share_token')
async def test_get_project_by_invalid_token(
    mock_get_project_by_share_token: AsyncMock,
    client: AsyncClient
):
    """Test accessing project with invalid share token"""
    from src.shares.exceptions import ShareTokenNotFoundException
    
    # Mock the service to raise exception
    mock_get_project_by_share_token.side_effect = ShareTokenNotFoundException()
    
    response = await client.get("/api/v1/projects/public/invalid-token")
    
    assert response.status_code == 404
    assert "Share token not found" in response.json()["detail"]


@pytest.mark.asyncio
@patch('src.shares.router.revoke_share')
async def test_revoke_share(
    mock_revoke_share: AsyncMock,
    client: AsyncClient,
    auth_headers: dict,
    sample_project: Project,
    sample_user_2: User
):
    """Test revoking a project share"""
    # Mock the service (revoke_share returns None on success)
    mock_revoke_share.return_value = None
    
    fake_share_id = str(uuid4())
    response = await client.delete(
        f"/api/v1/projects/shares/{fake_share_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
@patch('src.shares.router.revoke_share')
async def test_revoke_nonexistent_share(
    mock_revoke_share: AsyncMock,
    client: AsyncClient,
    auth_headers: dict
):
    """Test revoking a non-existent share"""
    from src.shares.exceptions import ShareNotFoundException
    
    # Mock the service to raise exception
    mock_revoke_share.side_effect = ShareNotFoundException()
    
    fake_share_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.delete(
        f"/api/v1/projects/shares/{fake_share_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "Share not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_access(
    client: AsyncClient,
    sample_project: Project
):
    """Test accessing share endpoints without authentication"""
    # Test creating public share without auth
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        json={}
    )
    assert response.status_code == 401
    
    # Test listing shares without auth
    response = await client.get(
        f"/api/v1/projects/{sample_project.project_id}/shares"
    )
    assert response.status_code == 401
    
    # Test listing shared projects without auth
    response = await client.get("/api/v1/users/me/shared-projects")
    assert response.status_code == 401


@pytest.mark.asyncio
@patch('src.shares.router.get_project_shares')
async def test_access_other_users_project_shares(
    mock_get_project_shares: AsyncMock,
    client: AsyncClient,
    auth_headers_2: dict,
    sample_project: Project
):
    """Test accessing another user's project shares (should fail)"""
    from src.projects.exceptions import ProjectNotFoundException
    
    # Mock the service to raise exception for unauthorized access
    mock_get_project_shares.side_effect = ProjectNotFoundException(project_id="test-id")
    
    response = await client.get(
        f"/api/v1/projects/{sample_project.project_id}/shares",
        headers=auth_headers_2
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
