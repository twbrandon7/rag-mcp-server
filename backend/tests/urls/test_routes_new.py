import uuid
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import URL, Project, User
from src.urls.constants import URLStatus


@pytest.fixture
async def authenticated_client(client: AsyncClient, db_session):
    """Fixture for a client with an authenticated user"""
    # Create a test user in the same session
    user_id = uuid.uuid4()
    user = User(
        user_id=user_id,
        email="test_url@example.com",
        password_hash="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    
    # Mock token creation
    token = "test_access_token_for_urls"
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": str(user_id)}
        
        # Return configured client
        client.headers["Authorization"] = f"Bearer {token}"
        yield client, user


async def test_submit_single_url(authenticated_client, db_session):
    """Test submitting a single URL."""
    client, user = authenticated_client
    
    # Create a test project via API instead of directly in db_session
    project_response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Project for URLs"}
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_data = project_response.json()
    project_id = project_data["project_id"]
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls",
        json={"original_url": "https://example.org/article1"}
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["original_url"] == "https://example.org/article1"
    assert data["status"] == URLStatus.PENDING.value
    assert "url_id" in data
    assert data["project_id"] == project_id


async def test_submit_duplicate_url(authenticated_client, db_session):
    """Test submitting a duplicate URL."""
    client, user = authenticated_client
    
    # Create a test project via API
    project_response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Project for URLs"}
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_data = project_response.json()
    project_id = project_data["project_id"]
    
    # Create a URL first via API
    first_response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls",
        json={"original_url": "https://example.com/test"}
    )
    assert first_response.status_code == status.HTTP_202_ACCEPTED
    first_url_data = first_response.json()
    
    # Try to submit the same URL again (should be duplicate)
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls",
        json={"original_url": "https://example.com/test"}
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "detail" in data
    assert "existing_url" in data["detail"]
    assert data["detail"]["existing_url"]["url_id"] == first_url_data["url_id"]


async def test_submit_multiple_urls(authenticated_client, db_session):
    """Test submitting multiple URLs at once."""
    client, user = authenticated_client
    
    # Create a test project via API
    project_response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Project for URLs"}
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_data = project_response.json()
    project_id = project_data["project_id"]
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls:batch",
        json={"urls": ["https://example.org/article2", "https://example.org/article3"]}
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "submitted_urls" in data
    assert "duplicate_urls" in data
    assert len(data["submitted_urls"]) == 2
    assert len(data["duplicate_urls"]) == 0


async def test_get_urls_in_project(authenticated_client, db_session):
    """Test getting all URLs in a project."""
    client, user = authenticated_client
    
    # Create a test project via API
    project_response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Project for URLs"}
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_data = project_response.json()
    project_id = project_data["project_id"]
    
    # Create a test URL via API
    url_response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls",
        json={"original_url": "https://example.com/test"}
    )
    assert url_response.status_code == status.HTTP_202_ACCEPTED
    url_data = url_response.json()
    
    response = await client.get(
        f"{settings.API_V1_STR}/projects/{project_id}/urls"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    
    response_url_data = data[0]
    # Verify all required fields are present according to API spec
    expected_fields = ["url_id", "project_id", "original_url", "status", "failure_reason", "submitted_at", "last_updated_at"]
    for field in expected_fields:
        assert field in response_url_data, f"Missing field: {field}"
    
    # Verify field values
    assert response_url_data["url_id"] == url_data["url_id"]
    assert response_url_data["project_id"] == project_id
    assert response_url_data["original_url"] == "https://example.com/test"
    assert response_url_data["status"] == URLStatus.PENDING.value


async def test_get_url_status(authenticated_client, db_session):
    """Test getting the status of a specific URL."""
    client, user = authenticated_client
    
    # Create a test project via API
    project_response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Project for URLs"}
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_data = project_response.json()
    project_id = project_data["project_id"]
    
    # Create a test URL via API
    url_response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls",
        json={"original_url": "https://example.com/test"}
    )
    assert url_response.status_code == status.HTTP_202_ACCEPTED
    url_data = url_response.json()
    url_id = url_data["url_id"]
    
    response = await client.get(
        f"{settings.API_V1_STR}/projects/{project_id}/urls/{url_id}"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url_id"] == url_id
    assert data["original_url"] == "https://example.com/test"
    assert data["status"] == URLStatus.PENDING.value


async def test_reprocess_url(authenticated_client, db_session):
    """Test reprocessing a URL."""
    client, user = authenticated_client
    
    # Create a test project via API
    project_response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Project for URLs"}
    )
    assert project_response.status_code == status.HTTP_201_CREATED
    project_data = project_response.json()
    project_id = project_data["project_id"]
    
    # Create a test URL via API
    url_response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls",
        json={"original_url": "https://example.com/test"}
    )
    assert url_response.status_code == status.HTTP_202_ACCEPTED
    url_data = url_response.json()
    url_id = url_data["url_id"]
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project_id}/urls/{url_id}:reprocess"
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["url_id"] == url_id
    assert data["status"] == URLStatus.PENDING.value
    assert data["failure_reason"] is None
