"""Chunk-related Pydantic schemas for request/response validation."""

from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ChunkResponse(BaseModel):
    """Response model for chunk data."""
    chunk_id: UUID
    url_id: UUID
    project_id: UUID
    content: str
    chunk_index: int
    created_at: datetime
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding (only included if requested)")


class ChunkQueryRequest(BaseModel):
    """Request model for querying chunks."""
    query: str = Field(..., min_length=1, max_length=1000, description="The query text for semantic similarity search")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of top results to return")


class ChunkQueryResult(BaseModel):
    """Single result from a chunk query."""
    chunk_id: UUID
    content: str
    similarity_score: float = Field(..., description="Similarity score between 0 and 1")
    chunk_index: int
    created_at: datetime


class ChunkQueryResponse(BaseModel):
    """Response model for chunk query results."""
    results: List[ChunkQueryResult]
