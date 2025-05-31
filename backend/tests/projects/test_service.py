import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Project
from src.projects.service import (
    create_project,
    get_project,
    get_user_projects,
    update_project,
    delete_project,
)
from src.projects.schemas import ProjectCreate, ProjectUpdate
from src.projects.exceptions import ProjectNotFoundException


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Fixture for a test user."""
    user_id = uuid.uuid4()
    email = "test_project_service@example.com"
    hashed_password = "hashed_password"
    
    # Create a user
    user = User(
        user_id=user_id,
        email=email,
        password_hash=hashed_password,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.mark.asyncio
async def test_create_project_service(db_session: AsyncSession, test_user: User):
    """Test create project service."""
    # Create a project
    project_data = ProjectCreate(project_name="Test Project Service")
    project = await create_project(db_session, test_user, project_data)
    
    # Verify project was created
    assert project is not None
    assert project.project_name == "Test Project Service"
    assert project.user_id == test_user.user_id
    assert isinstance(project.project_id, uuid.UUID)


@pytest.mark.asyncio
async def test_get_project_service(db_session: AsyncSession, test_user: User):
    """Test get project service."""
    # Create a project
    project_name = "Project to Get Service"
    project = Project(
        project_name=project_name,
        user_id=test_user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Get the project
    retrieved_project = await get_project(db_session, test_user.user_id, project.project_id)
    
    # Verify project was retrieved
    assert retrieved_project is not None
    assert retrieved_project.project_id == project.project_id
    assert retrieved_project.project_name == project_name


@pytest.mark.asyncio
async def test_get_project_service_not_found(db_session: AsyncSession, test_user: User):
    """Test get project service when project doesn't exist."""
    # Try to get a nonexistent project
    with pytest.raises(ProjectNotFoundException):
        await get_project(db_session, test_user.user_id, uuid.uuid4())


@pytest.mark.asyncio
async def test_get_user_projects_service(db_session: AsyncSession, test_user: User):
    """Test get user projects service."""
    # Create a few projects for the user
    project_names = ["Service Project 1", "Service Project 2", "Service Project 3"]
    projects = []
    
    for name in project_names:
        project = Project(
            project_name=name,
            user_id=test_user.user_id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        projects.append(project)
    
    await db_session.commit()
    
    # Get user projects
    retrieved_projects = await get_user_projects(db_session, test_user.user_id)
    
    # Verify projects were retrieved
    assert len(retrieved_projects) == len(project_names)
    retrieved_names = [p.project_name for p in retrieved_projects]
    assert sorted(retrieved_names) == sorted(project_names)


@pytest.mark.asyncio
async def test_update_project_service(db_session: AsyncSession, test_user: User):
    """Test update project service."""
    # Create a project
    project_name = "Project to Update Service"
    project = Project(
        project_name=project_name,
        user_id=test_user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Update the project
    update_data = ProjectUpdate(project_name="Updated Service Project Name")
    updated_project = await update_project(db_session, project, update_data)
    
    # Verify project was updated
    assert updated_project.project_name == "Updated Service Project Name"
    assert updated_project.project_id == project.project_id
    
    # Verify database was updated
    await db_session.refresh(project)
    assert project.project_name == "Updated Service Project Name"


@pytest.mark.asyncio
async def test_delete_project_service(db_session: AsyncSession, test_user: User):
    """Test delete project service."""
    # Create a project
    project_name = "Project to Delete Service"
    project = Project(
        project_name=project_name,
        user_id=test_user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Delete the project
    await delete_project(db_session, project)
    
    # Verify project is deleted
    with pytest.raises(ProjectNotFoundException):
        await get_project(db_session, test_user.user_id, project.project_id)
