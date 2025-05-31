import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from src.users.schemas import UserCreate, UserResponse
from src.models import User
from src.auth.utils import verify_password


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint."""
    # Prepare test data
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    # Send request to register endpoint
    response = await client.post("/api/v1/users", json=user_data)
    
    # Validate response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "user_id" in data
    assert "created_at" in data
    assert uuid.UUID(data["user_id"]) is not None


@pytest.mark.asyncio
async def test_register_user_email_exists(client: AsyncClient, db_session: AsyncSession):
    """Test user registration with an email that already exists."""
    # Create a user first
    email = "existing@example.com"
    password = "testpassword123"
    
    hashed_password = "hashed_password"  # This will be mocked
    
    # Mock the password hash function
    with patch("src.users.service.get_password_hash", return_value=hashed_password):
        # Create an existing user
        existing_user = User(email=email, password_hash=hashed_password)
        db_session.add(existing_user)
        await db_session.commit()
    
    # Try to register with the same email
    user_data = {
        "email": email,
        "password": password
    }
    
    # Send request
    response = await client.post("/api/v1/users", json=user_data)
    
    # Should return conflict error (409)
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_current_user_info(client: AsyncClient, db_session: AsyncSession):
    """Test get current user endpoint."""
    # Create a test user
    email = "user@example.com"
    password = "testpassword123"
    user_id = uuid.uuid4()
    
    # Mock the token verification
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        # Set up the mock to return a valid payload
        mock_decode.return_value = {"sub": str(user_id)}
        
        # Create a test user in the database
        test_user = User(
            user_id=user_id,
            email=email,
            password_hash="hashed_password",
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(test_user)
        await db_session.commit()
        
        # Make request to me endpoint with a fake token
        response = await client.get(
            "/api/v1/users/me", 
            headers={"Authorization": "Bearer fake_token_for_test"}
        )
        
        # Validate response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(user_id)
        assert "created_at" in data


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test get current user endpoint without authentication."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
