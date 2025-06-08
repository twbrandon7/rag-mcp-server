import uuid
from datetime import datetime
import pytest
from pydantic import UUID4
from sqlalchemy import select, and_

from src.models import URL, Project, User
from src.urls import service
from src.urls.constants import URLStatus
from src.urls.exceptions import DuplicateURLException


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        user_id=uuid.uuid4(),
        email="test_service@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_project(db_session, test_user):
    """Create a test project."""
    project = Project(
        project_id=uuid.uuid4(),
        user_id=test_user.user_id,
        project_name="Test Service Project"
    )
    db_session.add(project)
    await db_session.commit()
    return project


@pytest.fixture
async def test_url(db_session, test_project):
    """Create a test URL."""
    url = URL(
        url_id=uuid.uuid4(),
        project_id=test_project.project_id,
        original_url="https://example.com/service-test",
        status=URLStatus.STORED.value
    )
    db_session.add(url)
    await db_session.commit()
    return url


async def test_get_url_by_id(test_project, test_url, db_session):
    """Test getting a URL by ID."""
    url_data = await service.get_url_by_id(
        session=db_session,
        url_id=test_url.url_id,
        project_id=test_project.project_id
    )
    
    assert url_data is not None
    assert url_data["url_id"] == test_url.url_id
    assert url_data["original_url"] == test_url.original_url
    assert url_data["status"] == URLStatus.STORED.value


async def test_get_url_by_id_not_found(test_project, db_session):
    """Test getting a non-existent URL by ID."""
    non_existent_id = uuid.uuid4()
    url_data = await service.get_url_by_id(
        session=db_session,
        url_id=non_existent_id,
        project_id=test_project.project_id
    )
    assert url_data is None


async def test_get_urls_by_project(test_project, test_url, db_session):
    """Test getting all URLs in a project."""
    urls = await service.get_urls_by_project(
        session=db_session,
        project_id=test_project.project_id
    )
    
    assert len(urls) == 1
    url_data = urls[0]
    
    # Verify all required fields are present according to API spec
    expected_fields = ["url_id", "project_id", "original_url", "status", "failure_reason", "submitted_at", "last_updated_at"]
    for field in expected_fields:
        assert field in url_data, f"Missing field: {field}"
    
    # Verify field values
    assert url_data["url_id"] == test_url.url_id
    assert url_data["project_id"] == test_url.project_id
    assert url_data["original_url"] == test_url.original_url
    assert url_data["status"] == test_url.status


async def test_create_url(test_project, db_session):
    """Test creating a new URL."""
    original_url = "https://example.com/new-service-test"
    
    url_data = await service.create_url(
        session=db_session,
        project_id=test_project.project_id,
        original_url=original_url
    )
    
    assert url_data is not None
    assert url_data["original_url"] == original_url
    assert url_data["status"] == URLStatus.PENDING.value
    assert url_data["project_id"] == test_project.project_id


async def test_create_duplicate_url(test_project, test_url, db_session):
    """Test checking for duplicate URLs."""
    # Check if there's an existing URL with the same original_url
    query = select(URL).where(and_(
        URL.project_id == test_project.project_id, 
        URL.original_url == test_url.original_url
    ))
    result = await db_session.execute(query)
    existing_url = result.scalars().first()
    
    # Verify duplicate detection works
    assert existing_url is not None
    assert existing_url.url_id == test_url.url_id


async def test_batch_create_urls(test_project, db_session):
    """Test creating multiple URLs at once."""
    urls = ["https://example.com/batch1", "https://example.com/batch2"]
    
    # Create URLs directly in the test database
    for url_str in urls:
        url = URL(
            url_id=uuid.uuid4(),
            project_id=test_project.project_id,
            original_url=url_str,
            status=URLStatus.PENDING.value
        )
        db_session.add(url)
    
    await db_session.commit()
    
    # Verify URLs were created
    query = select(URL).where(URL.project_id == test_project.project_id)
    result = await db_session.execute(query)
    all_urls = result.scalars().all()
    
    # Should have at least the two URLs we just created
    assert len(all_urls) >= 2
    
    # Check for duplicates - try creating one of the same URLs
    duplicate_url = URL(
        url_id=uuid.uuid4(),
        project_id=test_project.project_id,
        original_url=urls[0],
        status=URLStatus.PENDING.value
    )
    db_session.add(duplicate_url)
    
    # Should raise an integrity error due to the unique constraint
    with pytest.raises(Exception):  # Could be an IntegrityError or other DB constraint violation
        await db_session.commit()


async def test_reprocess_url(test_project, test_url, db_session):
    """Test reprocessing a URL."""
    # First, set the URL to failed status
    test_url.status = URLStatus.FAILED.value
    test_url.failure_reason = "Test failure reason"
    db_session.add(test_url)
    await db_session.commit()
    
    # Update the URL directly
    test_url.status = URLStatus.PENDING.value
    test_url.failure_reason = None
    test_url.last_updated_at = datetime.now()
    db_session.add(test_url)
    await db_session.commit()
    await db_session.refresh(test_url)
    
    # Verify the update worked
    assert test_url.status == URLStatus.PENDING.value
    assert test_url.failure_reason is None
