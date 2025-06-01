"""Chunk-related exceptions."""

from fastapi import HTTPException, status


class ChunkNotFoundException(HTTPException):
    """Exception raised when a chunk is not found."""
    def __init__(self, detail: str = "Chunk not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": detail, "code": "CHUNK_NOT_FOUND"},
        )


class ChunkProcessingException(HTTPException):
    """Exception raised when chunk processing fails."""
    def __init__(self, detail: str = "Chunk processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": detail, "code": "CHUNK_PROCESSING_FAILED"},
        )


class InvalidQueryException(HTTPException):
    """Exception raised when query parameters are invalid."""
    def __init__(self, detail: str = "Invalid query parameters"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": detail, "code": "INVALID_QUERY"},
        )
