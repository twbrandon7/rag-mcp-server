import uuid
import pytest
from fastapi import HTTPException

from src.urls.dependencies import validate_url, validate_url_status
from src.urls.exceptions import InvalidURLFormatException, InvalidURLStatusException


def test_validate_url_valid():
    """Test validating a valid URL."""
    valid_urls = [
        "example.com",
        "http://example.com",
        "https://example.com",
        "https://example.com/path",
        "https://example.com/path?query=value",
        "https://example.com/path?query=value#fragment",
        "https://sub.example.com",
        "https://sub.example.co.uk",
        "http://localhost",
        "http://localhost:8000",
        "https://192.168.1.1",
        "https://192.168.1.1:8080"
    ]
    
    for url in valid_urls:
        result = validate_url(url)
        assert "http" in result  # Should have http/https scheme


def test_validate_url_invalid():
    """Test validating an invalid URL."""
    invalid_urls = [
        "not a url",
        "http://",
        "https://",
        "ftp://example.com",  # Not HTTP/HTTPS
        "@example.com",
        "example",  # No TLD
    ]
    
    for url in invalid_urls:
        with pytest.raises(InvalidURLFormatException):
            validate_url(url)


def test_validate_url_status_valid():
    """Test validating a valid URL status."""
    valid_statuses = ["pending", "crawling", "encoding", "stored", "failed", None]
    
    for status in valid_statuses:
        result = validate_url_status(status)
        assert result == status


def test_validate_url_status_invalid():
    """Test validating an invalid URL status."""
    invalid_statuses = ["invalid", "processing", "complete", "error"]
    
    for status in invalid_statuses:
        with pytest.raises(InvalidURLStatusException):
            validate_url_status(status)
