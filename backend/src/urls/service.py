import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import UUID4
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from src.database import engine
from src.models import URL, Project
from src.urls.constants import URLStatus
from src.urls.exceptions import DuplicateURLException


async def get_url_by_id(session: AsyncSession, url_id: UUID4, project_id: UUID4) -> Optional[Dict[str, Any]]:
    """Get a URL by ID."""
    query = select(URL).where(and_(URL.url_id == url_id, URL.project_id == project_id))
    result = await session.execute(query)
    url = result.scalars().first()
    
    if url:
        return {
            "url_id": url.url_id,
            "project_id": url.project_id,
            "original_url": url.original_url,
            "status": url.status,
            "failure_reason": url.failure_reason,
            "submitted_at": url.submitted_at,
            "last_updated_at": url.last_updated_at
        }
    return None


async def get_urls_by_project(session: AsyncSession, project_id: UUID4, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all URLs in a project, optionally filtering by status."""
    query = select(URL.url_id, URL.last_updated_at).where(URL.project_id == project_id)
    
    if status:
        query = query.where(URL.status == status)
        
    result = await session.execute(query)
    urls = result.all()
    
    return [{"url_id": url.url_id, "last_updated_at": url.last_updated_at} for url in urls]


async def create_url(session: AsyncSession, project_id: UUID4, original_url: str) -> Dict[str, Any]:
    """Create a new URL for processing."""
    # First, check if the URL already exists in this project
    query = select(URL).where(and_(URL.project_id == project_id, URL.original_url == original_url))
    result = await session.execute(query)
    existing_url = result.scalars().first()
    
    if existing_url:
        raise DuplicateURLException(
            existing_url={
                "url_id": str(existing_url.url_id),
                "project_id": str(existing_url.project_id),
                "last_updated_at": existing_url.last_updated_at.isoformat()
            }
        )
    
    # Create the URL
    now = datetime.now()
    url = URL(
        url_id=uuid.uuid4(),
        project_id=project_id,
        original_url=original_url,
        status=URLStatus.PENDING.value,
        submitted_at=now,
        last_updated_at=now
    )
    
    session.add(url)
    await session.commit()
    await session.refresh(url)
    
    return {
        "url_id": url.url_id,
        "project_id": url.project_id,
        "original_url": url.original_url,
        "status": url.status,
        "failure_reason": url.failure_reason,
        "submitted_at": url.submitted_at,
        "last_updated_at": url.last_updated_at
    }


async def batch_create_urls(session: AsyncSession, project_id: UUID4, urls: List[str]) -> Dict[str, Any]:
    """Create multiple URLs for processing."""
    submitted_urls = []
    duplicate_urls = []
    
    for original_url in urls:
        # Check if URL already exists in this project
        query = select(URL).where(and_(URL.project_id == project_id, URL.original_url == original_url))
        result = await session.execute(query)
        existing_url = result.scalars().first()
        
        if existing_url:
            duplicate_urls.append({
                "url_id": existing_url.url_id,
                "project_id": existing_url.project_id,
                "last_updated_at": existing_url.last_updated_at
            })
            continue
            
        # Create new URL
        now = datetime.now()
        url = URL(
            url_id=uuid.uuid4(),
            project_id=project_id,
            original_url=original_url,
            status=URLStatus.PENDING.value,
            submitted_at=now,
            last_updated_at=now
        )
        
        session.add(url)
        await session.flush()  # Flush to get the generated URL ID
        
        submitted_urls.append({
            "url_id": url.url_id,
            "project_id": url.project_id,
            "original_url": url.original_url,
            "status": url.status,
            "failure_reason": url.failure_reason,
            "submitted_at": url.submitted_at,
            "last_updated_at": url.last_updated_at
        })
    
    await session.commit()
    
    return {
        "submitted_urls": submitted_urls,
        "duplicate_urls": duplicate_urls
    }


async def reprocess_url(session: AsyncSession, url_id: UUID4, project_id: UUID4) -> Dict[str, Any]:
    """Reset URL status to pending for reprocessing."""
    # First get the URL
    query = select(URL).where(and_(URL.url_id == url_id, URL.project_id == project_id))
    result = await session.execute(query)
    url = result.scalars().first()
    
    if url:
        # Update the URL status
        now = datetime.now()
        url.status = URLStatus.PENDING.value
        url.failure_reason = None
        url.last_updated_at = now
        
        await session.commit()
        await session.refresh(url)
    
    return {
        "url_id": url.url_id,
        "project_id": url.project_id,
        "original_url": url.original_url,
        "status": url.status,
        "failure_reason": url.failure_reason,
        "submitted_at": url.submitted_at,
        "last_updated_at": url.last_updated_at
    }
