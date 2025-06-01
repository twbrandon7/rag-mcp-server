# Test to verify database override is working
import uuid
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import User, Project


@pytest.fixture
async def simple_authenticated_client(client: AsyncClient, db_session):
    """Simple fixture for a client with an authenticated user"""
    # Create a test user in the same session used by the fixture
    user_id = uuid.uuid4()
    user = User(
        user_id=user_id,
        email="test_simple@example.com", 
        password_hash="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    
    # Mock token for authentication
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": str(user_id)}
        client.headers["Authorization"] = f"Bearer test_token"
        yield client, user


async def test_simple_database_connection(simple_authenticated_client):
    """Test that API and test use the same database."""
    client, user = simple_authenticated_client
    
    # Try to create a project via API
    response = await client.post(
        f"{settings.API_V1_STR}/projects",
        json={"project_name": "Test Database Connection"}
    )
    
    print(f"Create project response: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code != 201:
        # If creation failed, let's see what happened
        assert False, f"Expected 201, got {response.status_code}: {response.text}"
    
    # Try to get projects via API
    response = await client.get(f"{settings.API_V1_STR}/projects")
    print(f"Get projects response: {response.status_code}")
    print(f"Response content: {response.text}")
    
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["project_name"] == "Test Database Connection"
