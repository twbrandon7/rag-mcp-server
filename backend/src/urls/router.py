from fastapi import APIRouter, Depends, Path, status
from typing import List, Optional
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_db
from src.projects.dependencies import get_project_by_id
from src.urls import service
from src.urls.constants import URLStatus
from src.urls.dependencies import get_url_or_404, validate_url, validate_url_status
from src.urls.schemas import (
    URLCreate, 
    URLBatchCreate, 
    URLResponse, 
    URLListResponse, 
    BatchSubmitResponse, 
    URLReprocessResponse
)
from src.chunks import service as chunk_service
from src.chunks.schemas import ChunkResponse, ChunkQueryRequest, ChunkQueryResponse
from src.chunks.dependencies import validate_include_vectors

router = APIRouter()


@router.post(
    "/{project_id}/urls", 
    response_model=URLResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a single URL",
    description="Submit a single URL for processing within a project."
)
async def submit_url(
    url_data: URLCreate,
    project = Depends(get_project_by_id),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    session: AsyncSession = Depends(get_db),
):
    """
    Submit a single URL for processing within a project.
    
    If the URL is already processed in this project, a 409 Conflict response
    will be returned with details of the existing URL entry.
    """
    # Validate and ensure URL has proper scheme
    validated_url = validate_url(url_data.original_url)
    
    # Create the URL
    url = await service.create_url(
        session=session,
        project_id=project_id,
        original_url=validated_url
    )
    
    return url


@router.post(
    "/{project_id}/urls:batch",
    response_model=BatchSubmitResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit multiple URLs",
    description="Submit multiple URLs for processing within a project."
)
async def submit_multiple_urls(
    urls_data: URLBatchCreate,
    project = Depends(get_project_by_id),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    session: AsyncSession = Depends(get_db),
):
    """
    Submit multiple URLs for processing within a project.
    
    Duplicate URLs (already processed in this project) will be filtered out
    and returned separately in the response.
    """
    validated_urls = [validate_url(url) for url in urls_data.urls]
    
    result = await service.batch_create_urls(
        session=session,
        project_id=project_id,
        urls=validated_urls
    )
    
    return result


@router.get(
    "/{project_id}/urls",
    response_model=List[URLListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get URLs in project",
    description="Get all URLs associated with a project."
)
async def get_urls(
    project = Depends(get_project_by_id),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    status: Optional[str] = Depends(validate_url_status),
    session: AsyncSession = Depends(get_db),
):
    """
    Get all URLs associated with a project.
    
    Optionally filter URLs by status (pending, crawling, encoding, stored, failed).
    """
    urls = await service.get_urls_by_project(session=session, project_id=project_id, status=status)
    return urls


@router.get(
    "/{project_id}/urls/{url_id}",
    response_model=URLResponse,
    status_code=status.HTTP_200_OK,
    summary="Get URL status",
    description="Get details and processing status of a specific URL."
)
async def get_url_status(
    url = Depends(get_url_or_404),
):
    """
    Get details and processing status of a specific URL.
    """
    return url


@router.post(
    "/{project_id}/urls/{url_id}:reprocess",
    response_model=URLReprocessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reprocess URL",
    description="Request reprocessing of a previously processed URL."
)
async def reprocess_url(
    url = Depends(get_url_or_404),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    url_id: UUID4 = Path(..., description="The ID of the URL to reprocess"),
    session: AsyncSession = Depends(get_db),
):
    """
    Request reprocessing of a previously processed URL.
    
    This will reset the URL status to 'pending' and clear any failure reason.
    """
    url = await service.reprocess_url(session=session, url_id=url_id, project_id=project_id)
    return url


# Content Chunks & Vectors endpoints

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
    chunks = await chunk_service.get_chunks_by_url(
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
    result = await chunk_service.query_chunks(
        session=session,
        url_id=url_id,
        project_id=project_id,
        query=query_data.query,
        top_k=query_data.top_k
    )
    return result
