"""Dependencies for chunk-related operations."""

from fastapi import Depends, Path, Query
from pydantic import UUID4
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_db
from src.urls.dependencies import get_url_or_404
from src.chunks.exceptions import InvalidQueryException


def validate_include_vectors(
    include_vectors: bool = Query(False, description="Include vector embeddings in response")
) -> bool:
    """Validate the include_vectors query parameter."""
    return include_vectors


def validate_query_params(
    query: str = None,
    top_k: int = Query(5, ge=1, le=50, description="Number of top results to return")
) -> tuple[str, int]:
    """Validate query parameters for chunk search."""
    if not query or len(query.strip()) == 0:
        raise InvalidQueryException("Query parameter is required and cannot be empty")
    
    if len(query.strip()) > 1000:
        raise InvalidQueryException("Query parameter cannot exceed 1000 characters")
    
    return query.strip(), top_k
