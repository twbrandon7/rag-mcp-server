import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user, get_optional_current_user
from src.auth.exceptions import InvalidTokenException, UserNotFoundException
from src.models import User


@pytest.mark.asyncio
async def test_get_current_user_success(db_session: AsyncSession):
    """Test retrieving the current user from a valid token."""
    # Create a test user
    user_id = uuid.uuid4()
    email = "current_user@example.com"
    test_user = User(
        user_id=user_id,
        email=email,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(test_user)
    await db_session.commit()
    
    # Mock token decoding
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        # Set up the mock to return a valid payload with user_id
        mock_decode.return_value = {"sub": str(user_id)}
        
        # Get current user using the mocked token
        user = await get_current_user("fake_token", db_session)
        
        # Verify the correct user is returned
        assert user is not None
        assert user.user_id == user_id
        assert user.email == email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session: AsyncSession):
    """Test retrieving the current user with an invalid token."""
    # Mock token decoding to raise an exception
    with patch("src.auth.dependencies.decode_access_token", side_effect=InvalidTokenException()):
        # Should raise InvalidTokenException
        with pytest.raises(InvalidTokenException):
            await get_current_user("invalid_token", db_session)


@pytest.mark.asyncio
async def test_get_current_user_missing_sub(db_session: AsyncSession):
    """Test retrieving the current user from a token with missing sub claim."""
    # Mock token decoding to return a payload without 'sub'
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"exp": 1625097600}  # Missing 'sub'
        
        # Should raise InvalidTokenException
        with pytest.raises(InvalidTokenException):
            await get_current_user("token_without_sub", db_session)


@pytest.mark.asyncio
async def test_get_current_user_invalid_uuid(db_session: AsyncSession):
    """Test retrieving the current user with an invalid UUID."""
    # Mock token decoding to return a payload with an invalid UUID
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": "not-a-valid-uuid"}
        
        # Should raise InvalidTokenException
        with pytest.raises(InvalidTokenException):
            await get_current_user("token_with_invalid_uuid", db_session)


@pytest.mark.asyncio
async def test_get_current_user_not_found(db_session: AsyncSession):
    """Test retrieving a non-existent user."""
    # Generate a random UUID that doesn't exist in the database
    non_existent_id = uuid.uuid4()
    
    # Mock token decoding
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        # Return a valid payload with non-existent user_id
        mock_decode.return_value = {"sub": str(non_existent_id)}
        
        # Should raise UserNotFoundException
        with pytest.raises(UserNotFoundException):
            await get_current_user("token_with_nonexistent_id", db_session)


@pytest.mark.asyncio
async def test_get_optional_current_user_exists(db_session: AsyncSession):
    """Test retrieving optional user when the user exists."""
    # Create a test user
    user_id = uuid.uuid4()
    email = "optional_user@example.com"
    test_user = User(
        user_id=user_id,
        email=email,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(test_user)
    await db_session.commit()
    
    # Mock get_current_user to return the test user
    with patch("src.auth.dependencies.get_current_user", return_value=test_user):
        # Get optional current user
        user = await get_optional_current_user("fake_token", db_session)
        
        # Verify the correct user is returned
        assert user is not None
        assert user.user_id == user_id
        assert user.email == email


@pytest.mark.asyncio
async def test_get_optional_current_user_not_authenticated(db_session: AsyncSession):
    """Test retrieving optional user when not authenticated."""
    # Mock get_current_user to raise an exception
    with patch("src.auth.dependencies.get_current_user", side_effect=InvalidTokenException()):
        # Get optional current user
        user = await get_optional_current_user("invalid_token", db_session)
        
        # Should return None instead of raising an exception
        assert user is None
