from enum import Enum, auto


class ErrorCode(str, Enum):
    """Error codes for URL operations."""
    URL_NOT_FOUND = "URL_NOT_FOUND"
    DUPLICATE_URL = "DUPLICATE_URL"
    INVALID_URL_FORMAT = "INVALID_URL_FORMAT"
    URL_PROCESSING_FAILED = "URL_PROCESSING_FAILED"
    INVALID_URL_STATUS = "INVALID_URL_STATUS"


class URLStatus(str, Enum):
    """Status of a URL in the processing pipeline."""
    PENDING = "pending"
    CRAWLING = "crawling"
    ENCODING = "encoding"
    STORED = "stored"
    FAILED = "failed"
