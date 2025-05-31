import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.auth.utils import verify_password, get_password_hash, create_access_token, decode_access_token
from src.auth.exceptions import InvalidTokenException
from src.auth.config import jwt_settings


def test_password_verification():
    """Test password verification."""
    # Mock password verification 
    with patch("src.auth.utils.pwd_context.verify", return_value=True):
        result = verify_password("plaintext_password", "hashed_password")
        assert result is True
    
    with patch("src.auth.utils.pwd_context.verify", return_value=False):
        result = verify_password("wrong_password", "hashed_password")
        assert result is False


def test_password_hashing():
    """Test password hashing."""
    # Mock hashing function
    expected_hash = "hashed_password_123"
    with patch("src.auth.utils.pwd_context.hash", return_value=expected_hash):
        result = get_password_hash("plaintext_password")
        assert result == expected_hash


def test_create_access_token():
    """Test JWT token creation."""
    # Test data
    user_id = "test-user-id"
    data = {"sub": user_id}
    
    # Create token with explicit expiry
    expires_delta = timedelta(minutes=30)
    with patch("src.auth.utils.jwt.encode", return_value="test_token"):
        token = create_access_token(data, expires_delta=expires_delta)
        assert token == "test_token"
    
    # Create token with default expiry
    with patch("src.auth.utils.jwt.encode", return_value="default_expiry_token"):
        token = create_access_token(data)
        assert token == "default_expiry_token"


def test_decode_access_token_valid():
    """Test decoding a valid JWT token."""
    # Mock jwt.decode to return a valid payload
    mock_payload = {"sub": "test-user", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
    
    with patch("src.auth.utils.jwt.decode", return_value=mock_payload):
        payload = decode_access_token("valid_token")
        assert payload == mock_payload
        assert payload["sub"] == "test-user"


def test_decode_access_token_invalid():
    """Test decoding an invalid JWT token."""
    # Mock jwt.decode to raise an exception
    with patch("src.auth.utils.jwt.decode", side_effect=jwt.InvalidTokenError("Invalid token")):
        with pytest.raises(InvalidTokenException):
            decode_access_token("invalid_token")


def test_decode_access_token_expired():
    """Test decoding an expired JWT token."""
    # Mock jwt.decode to raise an expiration exception
    with patch("src.auth.utils.jwt.decode", side_effect=jwt.ExpiredSignatureError("Token expired")):
        with pytest.raises(InvalidTokenException):
            decode_access_token("expired_token")
