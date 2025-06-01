"""Chunks router for content chunk and vector operations."""

from fastapi import APIRouter, Depends, Path, status
from typing import List
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_db
from src.urls.dependencies import get_url_or_404
from src.chunks import service
from src.chunks.schemas import ChunkResponse, ChunkQueryRequest, ChunkQueryResponse
from src.chunks.dependencies import validate_include_vectors

router = APIRouter()


@router.get(
    "/{project_id}/urls/{url_id}/chunks",
    response_model=List[ChunkResponse],
    status_code=status.HTTP_200_OK,
    summary="Get content chunks for URL",
    description="Retrieve the content chunks associated with a processed URL."
)
async def get_content_chunks(
    url = Depends(get_url_or_404),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    url_id: UUID4 = Path(..., description="The ID of the URL"),
    include_vectors: bool = Depends(validate_include_vectors),
    session: AsyncSession = Depends(get_db),
) -> List[ChunkResponse]:
    """
    Retrieve the content chunks associated with a processed URL.
    
    Optionally include vector embeddings in the response by setting include_vectors=true.
    """
    chunks = await service.get_chunks_by_url(
        session=session,
        url_id=url_id,
        project_id=project_id,
        include_vectors=include_vectors
    )
    return chunks


@router.post(
    "/{project_id}/urls/{url_id}/chunks:query",
    response_model=ChunkQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query content chunks",
    description="Perform a semantic similarity query on the content chunks of a specific URL."
)
async def query_content_chunks(
    query_data: ChunkQueryRequest,
    url = Depends(get_url_or_404),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    url_id: UUID4 = Path(..., description="The ID of the URL"),
    session: AsyncSession = Depends(get_db),
) -> ChunkQueryResponse:
    """
    Perform a semantic similarity query on the content chunks of a specific URL.
    
    Returns the most relevant chunks based on semantic similarity to the query text.
    Note: This is currently a placeholder implementation.
    """
    result = await service.query_chunks(
        session=session,
        url_id=url_id,
        project_id=project_id,
        query=query_data.query,
        top_k=query_data.top_k
    )
    return result
