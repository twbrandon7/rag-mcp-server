# filepath: /workspaces/rag-mcp-server/backend/tests/auth/test_router.py
import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.auth.schemas import Token
from src.auth.exceptions import InvalidCredentialsException


@pytest.mark.asyncio
async def test_login_success_mock(client: AsyncClient):
    """Test successful login with mocked dependencies."""
    email = "login_test@example.com"
    password = "securepassword123"
    user_id = uuid.uuid4()
    
    # Create a mock user
    test_user = User(
        user_id=user_id,
        email=email,
        password_hash="mock_hash",
        created_at=datetime.now(timezone.utc)
    )
    
    # Mock the authenticate_user function in auth service
    with patch("src.auth.router.authenticate_user") as mock_auth:
        mock_auth.return_value = test_user
        
        # Mock token creation
        mock_token = "test_access_token"
        with patch("src.auth.service.create_access_token", return_value=mock_token):
            # Login using form data format
            form_data = {
                "username": email,  # OAuth2 uses username for the email
                "password": password,
            }
            
            # Send login request
            response = await client.post(
                "/api/v1/auth/token",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Verify response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    # Mock authentication to fail
    with patch("src.auth.service.authenticate_user", side_effect=InvalidCredentialsException()):
        # Login with invalid credentials
        form_data = {
            "username": "invalid@example.com",
            "password": "wrongpassword",
        }
        
        # Send login request
        response = await client.post(
            "/api/v1/auth/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should return unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_google_oauth_login(client: AsyncClient, db_session: AsyncSession):
    """Test login with Google OAuth token."""
    # Test data
    oauth_token = "google_oauth_token"
    email = "google_user@example.com"
    user_id = uuid.uuid4()
    
    # Mock the OAuth validation function
    with patch("src.auth.service.validate_oauth_token") as mock_validate:
        # Set up the mock to return a user
        test_user = User(
            user_id=user_id,
            email=email,
            google_id="google_123456789",
            created_at=datetime.now(timezone.utc)
        )
        mock_validate.return_value = test_user
        
        # Mock the token creation
        with patch("src.auth.service.create_user_token") as mock_token_create:
            mock_token = "google_access_token"
            mock_token_create.return_value = Token(access_token=mock_token)
            
            # Send request with OAuth token
            response = await client.post(
                "/api/v1/auth/google",
                json={"token": oauth_token}
            )
            
            # Verify the response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_microsoft_oauth_login(client: AsyncClient, db_session: AsyncSession):
    """Test login with Microsoft OAuth token."""
    # Test data
    oauth_token = "microsoft_oauth_token"
    email = "microsoft_user@example.com"
    user_id = uuid.uuid4()
    
    # Mock the OAuth validation function
    with patch("src.auth.service.validate_oauth_token") as mock_validate:
        # Set up the mock to return a user
        test_user = User(
            user_id=user_id,
            email=email,
            microsoft_id="microsoft_123456789",
            created_at=datetime.now(timezone.utc)
        )
        mock_validate.return_value = test_user
        
        # Mock the token creation
        with patch("src.auth.service.create_user_token") as mock_token_create:
            mock_token = "microsoft_access_token"
            mock_token_create.return_value = Token(access_token=mock_token)
            
            # Send request with OAuth token
            response = await client.post(
                "/api/v1/auth/microsoft",
                json={"token": oauth_token}
            )
            
            # Verify the response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
