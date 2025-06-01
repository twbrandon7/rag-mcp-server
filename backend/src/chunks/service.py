"""Chunk service layer for business logic."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import Chunk
from src.chunks.schemas import ChunkResponse, ChunkQueryResponse, ChunkQueryResult
from src.chunks.exceptions import ChunkNotFoundException


async def get_chunks_by_url(
    session: AsyncSession,
    url_id: UUID,
    project_id: UUID,
    include_vectors: bool = False
) -> List[ChunkResponse]:
    """
    Get all chunks for a specific URL.
    
    Args:
        session: Database session
        url_id: ID of the URL
        project_id: ID of the project (for access control)
        include_vectors: Whether to include vector embeddings in response
        
    Returns:
        List of chunk responses
    """
    # Query chunks for the specific URL and project
    stmt = select(Chunk).where(
        Chunk.url_id == url_id,
        Chunk.project_id == project_id
    ).order_by(Chunk.chunk_index)
    
    result = await session.execute(stmt)
    chunks = result.scalars().all()
    
    # Convert to response models
    chunk_responses = []
    for chunk in chunks:
        chunk_response = ChunkResponse(
            chunk_id=chunk.chunk_id,
            url_id=chunk.url_id,
            project_id=chunk.project_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            created_at=chunk.created_at,
            embedding=chunk.embedding if include_vectors else None
        )
        chunk_responses.append(chunk_response)
    
    return chunk_responses


async def query_chunks(
    session: AsyncSession,
    url_id: UUID,
    project_id: UUID,
    query: str,
    top_k: int = 5
) -> ChunkQueryResponse:
    """
    Perform semantic similarity search on chunks for a specific URL.
    
    Args:
        session: Database session
        url_id: ID of the URL
        project_id: ID of the project (for access control)
        query: The query text for similarity search
        top_k: Number of top results to return
        
    Returns:
        Query response with similarity results
    """
    # PLACEHOLDER: This is a complex implementation that would involve:
    # 1. Converting the query text to a vector embedding using the same model
    # 2. Performing vector similarity search using pgvector's capabilities
    # 3. Returning results sorted by similarity score
    
    # For now, return a placeholder response
    # TODO: Implement actual vector similarity search
    
    # Query existing chunks to return as placeholder
    stmt = select(Chunk).where(
        Chunk.url_id == url_id,
        Chunk.project_id == project_id
    ).order_by(Chunk.chunk_index).limit(top_k)
    
    result = await session.execute(stmt)
    chunks = result.scalars().all()
    
    # Create placeholder results with dummy similarity scores
    query_results = []
    for i, chunk in enumerate(chunks):
        # Placeholder similarity score (decreasing from 1.0)
        similarity_score = 1.0 - (i * 0.1)
        
        query_result = ChunkQueryResult(
            chunk_id=chunk.chunk_id,
            content=chunk.content,
            similarity_score=similarity_score,
            chunk_index=chunk.chunk_index,
            created_at=chunk.created_at
        )
        query_results.append(query_result)
    
    return ChunkQueryResponse(results=query_results)
