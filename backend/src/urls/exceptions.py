from fastapi import HTTPException, status

from src.urls.constants import ErrorCode


class URLNotFoundException(HTTPException):
    """Exception raised when a URL is not found."""
    
    def __init__(self, detail: str = "URL not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": detail, "code": ErrorCode.URL_NOT_FOUND},
        )


class DuplicateURLException(HTTPException):
    """Exception raised when a duplicate URL is submitted."""
    
    def __init__(self, detail: str = "URL already exists in this project", existing_url=None):
        response_detail = {"message": detail, "code": ErrorCode.DUPLICATE_URL}
        if existing_url:
            response_detail["existing_url"] = existing_url
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_detail,
        )


class InvalidURLFormatException(HTTPException):
    """Exception raised when the URL format is invalid."""
    
    def __init__(self, detail: str = "Invalid URL format"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": detail, "code": ErrorCode.INVALID_URL_FORMAT},
        )


class URLProcessingFailedException(HTTPException):
    """Exception raised when URL processing fails."""
    
    def __init__(self, detail: str = "URL processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": detail, "code": ErrorCode.URL_PROCESSING_FAILED},
        )


class InvalidURLStatusException(HTTPException):
    """Exception raised when an invalid URL status is provided."""
    
    def __init__(self, detail: str = "Invalid URL status"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": detail, "code": ErrorCode.INVALID_URL_STATUS},
        )
