import re
from fastapi import Depends, Path, Query
from pydantic import UUID4
from typing import Optional, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_db
from src.projects.dependencies import get_project_by_id
from src.urls.constants import URLStatus
from src.urls.exceptions import InvalidURLFormatException, InvalidURLStatusException, URLNotFoundException
from src.urls import service


def validate_url(url: str) -> str:
    """Validate URL format."""
    url_pattern = re.compile(
        r'^(https?://)?' # http:// or https://
        r'((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|' # domain name like example.com
        r'localhost|' # or localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # or IP address
        r'(:\d+)?' # optional port
        r'(/[-a-z\d%_.~+]*)*' # path
        r'(\?[;&a-z\d%_.~+=-]*)?' # query string
        r'(\#[-a-z\d_]*)?$', # fragment locator
        re.IGNORECASE
    )
    if not url_pattern.match(url):
        raise InvalidURLFormatException(f"Invalid URL format: {url}")
    
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    return url


def validate_url_status(status: Optional[str] = Query(None)) -> Optional[str]:
    """Validate URL status query parameter."""
    if status is not None and status not in [s.value for s in URLStatus]:
        valid_statuses = ', '.join([s.value for s in URLStatus])
        raise InvalidURLStatusException(f"Invalid status. Valid values are: {valid_statuses}")
    return status


async def get_url_or_404(
    url_id: UUID4 = Path(..., description="The ID of the URL to retrieve"),
    project_id: UUID4 = Path(..., description="The ID of the project"),
    project = Depends(get_project_by_id),
    session: AsyncSession = Depends(get_db)
) -> dict:
    """Dependency to get a URL by ID or raise a 404 error."""
    url = await service.get_url_by_id(session=session, url_id=url_id, project_id=project_id)
    if not url:
        raise URLNotFoundException(f"URL with ID {url_id} not found in project {project_id}")
    return url
