import pytest
from uuid import uuid4
from httpx import AsyncClient

from src.models import User, Project


@pytest.mark.asyncio
async def test_create_public_share_token(client: AsyncClient, auth_headers: dict, sample_project: Project):
    """Test creating a public share token"""
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "share_id" in data
    assert "project_id" in data
    assert "share_token" in data
    assert "created_at" in data
    assert data["project_id"] == str(sample_project.project_id)
    assert len(data["share_token"]) > 10


@pytest.mark.asyncio
async def test_create_public_share_token_duplicate(client: AsyncClient, auth_headers: dict, sample_project: Project):
    """Test creating duplicate public share token returns conflict"""
    # Create first share
    await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        headers=auth_headers,
        json={}
    )
    
    # Try to create another
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 409
    assert "already has a public share token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_public_share_token_project_not_found(client: AsyncClient, auth_headers: dict):
    """Test creating public share for non-existent project"""
    non_existent_project_id = uuid4()
    
    response = await client.post(
        f"/api/v1/projects/{non_existent_project_id}/shares/public",
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_public_share_token_unauthorized(client: AsyncClient, sample_project: Project):
    """Test creating public share without authentication"""
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        json={}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_share_project_with_user(client: AsyncClient, auth_headers: dict, sample_project: Project, sample_user_2: User):
    """Test sharing project with another user"""
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(sample_user_2.user_id)}
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
async def test_share_project_with_user_duplicate(client: AsyncClient, auth_headers: dict, sample_project: Project, sample_user_2: User):
    """Test sharing with same user twice returns conflict"""
    # Share first time
    await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(sample_user_2.user_id)}
    )
    
    # Try to share again
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(sample_user_2.user_id)}
    )
    
    assert response.status_code == 409
    assert "already shared with this user" in response.json()["detail"]


@pytest.mark.asyncio
async def test_share_project_with_self(client: AsyncClient, auth_headers: dict, sample_project: Project, sample_user: User):
    """Test sharing project with self returns bad request"""
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(sample_user.user_id)}
    )
    
    assert response.status_code == 400
    assert "Cannot share project with yourself" in response.json()["detail"]


@pytest.mark.asyncio
async def test_share_project_with_nonexistent_user(client: AsyncClient, auth_headers: dict, sample_project: Project):
    """Test sharing with non-existent user"""
    non_existent_user_id = uuid4()
    
    response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(non_existent_user_id)}
    )
    
    assert response.status_code == 404
    assert "Target user not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_project_shares(client: AsyncClient, auth_headers: dict, sample_project: Project, sample_user_2: User):
    """Test listing project shares"""
    # Create public share and user share
    await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        headers=auth_headers,
        json={}
    )
    await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(sample_user_2.user_id)}
    )
    
    response = await client.get(
        f"/api/v1/projects/{sample_project.project_id}/shares",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    public_share = next((s for s in data if s["share_token"] is not None), None)
    user_share = next((s for s in data if s["shared_with_user_id"] is not None), None)
    
    assert public_share is not None
    assert user_share is not None
    assert user_share["shared_with_user_id"] == str(sample_user_2.user_id)


@pytest.mark.asyncio
async def test_list_shared_projects(client: AsyncClient, auth_headers_2: dict, sample_project: Project, sample_user_2: User):
    """Test listing projects shared with current user"""
    # First, share the project with user_2 using user_1's auth
    user_1_auth = await client.post("/api/v1/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    user_1_headers = {"Authorization": f"Bearer {user_1_auth.json()['access_token']}"}
    
    await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=user_1_headers,
        json={"shared_with_user_id": str(sample_user_2.user_id)}
    )
    
    # Now get shared projects for user_2
    response = await client.get(
        "/api/v1/users/me/shared-projects",
        headers=auth_headers_2
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["project_id"] == str(sample_project.project_id)
    assert data[0]["project_name"] == sample_project.project_name


@pytest.mark.asyncio
async def test_get_project_by_public_token(client: AsyncClient, auth_headers: dict, sample_project: Project):
    """Test getting project info by public share token"""
    # Create public share
    share_response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/public",
        headers=auth_headers,
        json={}
    )
    share_token = share_response.json()["share_token"]
    
    # Get project by token (no auth required)
    response = await client.get(f"/api/v1/projects/public/{share_token}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == str(sample_project.project_id)
    assert data["project_name"] == sample_project.project_name


@pytest.mark.asyncio
async def test_get_project_by_invalid_token(client: AsyncClient):
    """Test getting project with invalid token"""
    response = await client.get("/api/v1/projects/public/invalid-token")
    
    assert response.status_code == 404
    assert "Share token not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_revoke_project_share(client: AsyncClient, auth_headers: dict, sample_project: Project, sample_user_2: User):
    """Test revoking a project share"""
    # Create share
    share_response = await client.post(
        f"/api/v1/projects/{sample_project.project_id}/shares/users",
        headers=auth_headers,
        json={"shared_with_user_id": str(sample_user_2.user_id)}
    )
    share_id = share_response.json()["share_id"]
    
    # Revoke share
    response = await client.delete(
        f"/api/v1/projects/shares/{share_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify share is gone
    shares_response = await client.get(
        f"/api/v1/projects/{sample_project.project_id}/shares",
        headers=auth_headers
    )
    assert len(shares_response.json()) == 0


@pytest.mark.asyncio
async def test_revoke_nonexistent_share(client: AsyncClient, auth_headers: dict):
    """Test revoking non-existent share"""
    non_existent_share_id = uuid4()
    
    response = await client.delete(
        f"/api/v1/projects/shares/{non_existent_share_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "Share not found" in response.json()["detail"]
