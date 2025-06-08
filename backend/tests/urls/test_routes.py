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
    
    # Create a test project in the same session
    project = Project(
        project_id=uuid.uuid4(),
        user_id=user.user_id,
        project_name="Test Project for URLs",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project.project_id}/urls",
        json={"original_url": "https://example.org/article1"}
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["original_url"] == "https://example.org/article1"
    assert data["status"] == URLStatus.PENDING.value
    assert "url_id" in data
    assert data["project_id"] == str(project.project_id)


async def test_submit_duplicate_url(authenticated_client, db_session):
    """Test submitting a duplicate URL."""
    client, user = authenticated_client
    
    # Create a test project in the same session
    project = Project(
        project_id=uuid.uuid4(),
        user_id=user.user_id,
        project_name="Test Project for URLs",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    
    # Create a test URL in the same session
    test_url = URL(
        url_id=uuid.uuid4(),
        project_id=project.project_id,
        original_url="https://example.com/test",
        status=URLStatus.STORED.value,
        submitted_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc)
    )
    db_session.add(test_url)
    await db_session.commit()
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project.project_id}/urls",
        json={"original_url": test_url.original_url}
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "detail" in data
    assert "existing_url" in data["detail"]
    assert data["detail"]["existing_url"]["url_id"] == str(test_url.url_id)


async def test_submit_multiple_urls(authenticated_client, db_session):
    """Test submitting multiple URLs at once."""
    client, user = authenticated_client
    
    # Create a test project in the same session
    project = Project(
        project_id=uuid.uuid4(),
        user_id=user.user_id,
        project_name="Test Project for URLs",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project.project_id}/urls:batch",
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
    
    # Create a test project in the same session
    project = Project(
        project_id=uuid.uuid4(),
        user_id=user.user_id,
        project_name="Test Project for URLs",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    
    # Create a test URL in the same session
    test_url = URL(
        url_id=uuid.uuid4(),
        project_id=project.project_id,
        original_url="https://example.com/test",
        status=URLStatus.STORED.value,
        submitted_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc)
    )
    db_session.add(test_url)
    await db_session.commit()
    
    response = await client.get(
        f"{settings.API_V1_STR}/projects/{project.project_id}/urls"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    
    url_data = data[0]
    # Verify all required fields are present according to API spec
    expected_fields = ["url_id", "project_id", "original_url", "status", "failure_reason", "submitted_at", "last_updated_at"]
    for field in expected_fields:
        assert field in url_data, f"Missing field: {field}"
    
    # Verify field values
    assert url_data["url_id"] == str(test_url.url_id)
    assert url_data["project_id"] == str(test_url.project_id)
    assert url_data["original_url"] == test_url.original_url
    assert url_data["status"] == test_url.status


async def test_get_url_status(authenticated_client, db_session):
    """Test getting the status of a specific URL."""
    client, user = authenticated_client
    
    # Create a test project in the same session
    project = Project(
        project_id=uuid.uuid4(),
        user_id=user.user_id,
        project_name="Test Project for URLs",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    
    # Create a test URL in the same session
    test_url = URL(
        url_id=uuid.uuid4(),
        project_id=project.project_id,
        original_url="https://example.com/test",
        status=URLStatus.STORED.value,
        submitted_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc)
    )
    db_session.add(test_url)
    await db_session.commit()
    
    response = await client.get(
        f"{settings.API_V1_STR}/projects/{project.project_id}/urls/{test_url.url_id}"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url_id"] == str(test_url.url_id)
    assert data["original_url"] == test_url.original_url
    assert data["status"] == URLStatus.STORED.value


async def test_reprocess_url(authenticated_client, db_session):
    """Test reprocessing a URL."""
    client, user = authenticated_client
    
    # Create a test project in the same session
    project = Project(
        project_id=uuid.uuid4(),
        user_id=user.user_id,
        project_name="Test Project for URLs",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    
    # Create a test URL in the same session
    test_url = URL(
        url_id=uuid.uuid4(),
        project_id=project.project_id,
        original_url="https://example.com/test",
        status=URLStatus.STORED.value,
        submitted_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc)
    )
    db_session.add(test_url)
    await db_session.commit()
    
    response = await client.post(
        f"{settings.API_V1_STR}/projects/{project.project_id}/urls/{test_url.url_id}:reprocess"
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["url_id"] == str(test_url.url_id)
    assert data["status"] == URLStatus.PENDING.value
    assert data["failure_reason"] is None
