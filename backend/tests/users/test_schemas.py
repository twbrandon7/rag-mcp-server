import pytest
from pydantic import ValidationError

from src.users.schemas import UserCreate, UserResponse


def test_user_create_valid_data():
    """Test validation of UserCreate schema with valid data."""
    # Valid data
    valid_data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    # Should validate without raising an exception
    user_create = UserCreate(**valid_data)
    assert user_create.email == valid_data["email"]
    assert user_create.password == valid_data["password"]


def test_user_create_invalid_email():
    """Test validation of UserCreate schema with invalid email."""
    # Invalid email formats
    invalid_emails = [
        "not-an-email",
        "missing-at-sign.com",
        "@missing-user.com",
        "user@.com",
        "user@domain."
    ]
    
    for invalid_email in invalid_emails:
        invalid_data = {
            "email": invalid_email,
            "password": "securepassword123"
        }
        
        # Should raise ValidationError
        with pytest.raises(ValidationError):
            UserCreate(**invalid_data)


def test_user_create_missing_fields():
    """Test validation of UserCreate schema with missing fields."""
    # Missing email
    missing_email = {
        "password": "securepassword123"
    }
    with pytest.raises(ValidationError):
        UserCreate(**missing_email)
    
    # Missing password
    missing_password = {
        "email": "test@example.com"
    }
    with pytest.raises(ValidationError):
        UserCreate(**missing_password)


def test_user_response_schema():
    """Test UserResponse schema."""
    # Test data
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    created_at = "2023-01-01T12:00:00"
    
    # Create response object - note that UserResponse doesn't include email field
    response_data = {
        "user_id": user_id,
        "created_at": created_at
    }
    
    # Should validate without raising an exception
    user_response = UserResponse(**response_data)
    assert str(user_response.user_id) == user_id
    assert user_response.created_at.isoformat() == created_at
    assert user_response.created_at.isoformat() == created_at
