from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4, HttpUrl, validator

from src.urls.constants import URLStatus


class URLBase(BaseModel):
    """Base schema for URL data."""
    original_url: str


class URLCreate(URLBase):
    """Schema for creating a new URL."""
    pass


class URLBatchCreate(BaseModel):
    """Schema for creating multiple URLs at once."""
    urls: List[str]


class URLResponse(URLBase):
    """Schema for URL response."""
    url_id: UUID4
    project_id: UUID4
    status: str
    failure_reason: Optional[str] = None
    submitted_at: datetime
    last_updated_at: datetime


class URLListResponse(BaseModel):
    """Schema for a URL in list response."""
    url_id: UUID4
    last_updated_at: datetime


class BatchSubmitResponse(BaseModel):
    """Schema for batch URL submission response."""
    submitted_urls: List[URLResponse]
    duplicate_urls: List[Dict[str, Any]]


class DuplicateURLResponse(BaseModel):
    """Schema for duplicate URL response."""
    message: str
    existing_url: Dict[str, Any]
    
    
class URLReprocessResponse(URLResponse):
    """Schema for URL reprocess response."""
    pass
