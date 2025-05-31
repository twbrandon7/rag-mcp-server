import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from src.users.schemas import UserCreate
from src.users.service import create_user, get_user_by_id
from src.auth.exceptions import EmailExistsException
from src.models import User


@pytest.mark.asyncio
async def test_create_user_success(db_session: AsyncSession):
    """Test successfully creating a new user."""
    # Create test data
    email = "newuser@example.com"
    password = "securepassword123"
    user_data = UserCreate(email=email, password=password)
    
    # Mock password hashing
    hashed_password = "hashed_password_for_test"
    
    with patch("src.users.service.get_password_hash", return_value=hashed_password):
        # Create user
        user = await create_user(db_session, user_data)
        
        # Assertions
        assert user is not None
        assert user.email == email
        assert user.password_hash == hashed_password
        assert user.user_id is not None
        assert user.created_at is not None


@pytest.mark.asyncio
async def test_create_user_email_exists(db_session: AsyncSession):
    """Test creating a user with an email that already exists."""
    # Create a user first
    email = "existing@example.com"
    existing_user = User(
        email=email,
        password_hash="some_hash"
    )
    db_session.add(existing_user)
    await db_session.commit()
    
    # Try creating another user with the same email
    user_data = UserCreate(email=email, password="anotherpassword")
    
    # Should raise EmailExistsException
    with pytest.raises(EmailExistsException):
        await create_user(db_session, user_data)


@pytest.mark.asyncio
async def test_get_user_by_id_found(db_session: AsyncSession):
    """Test finding a user by ID."""
    # Create test user
    user_id = uuid.uuid4()
    email = "findme@example.com"
    test_user = User(
        user_id=user_id,
        email=email,
        password_hash="some_hash"
    )
    db_session.add(test_user)
    await db_session.commit()
    
    # Find the user using UUID object instead of string
    found_user = await get_user_by_id(db_session, user_id)
    
    # Assertions
    assert found_user is not None
    assert found_user.user_id == user_id
    assert found_user.email == email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session: AsyncSession):
    """Test not finding a user with non-existent ID."""
    # Use UUID object instead of string
    non_existent_id = uuid.uuid4()
    found_user = await get_user_by_id(db_session, non_existent_id)
    assert found_user is None
