import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from src.models import User, Project
from src.projects.schemas import ProjectCreate, ProjectResponse


@pytest.fixture
async def authenticated_client(client: AsyncClient, db_session: AsyncSession):
    """Fixture for a client with an authenticated user"""
    # Create a test user
    user_id = uuid.uuid4()
    email = "test_project_user@example.com"
    hashed_password = "hashed_password"  # This will be mocked
    
    # Create a user
    user = User(
        user_id=user_id,
        email=email,
        password_hash=hashed_password,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    
    # Mock token creation
    token = "test_access_token_for_projects"
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": str(user_id)}
        
        # Return configured client
        client.headers["Authorization"] = f"Bearer {token}"
        yield client, user


@pytest.mark.asyncio
async def test_create_project(authenticated_client, db_session: AsyncSession):
    """Test creating a new project."""
    client, user = authenticated_client
    
    # Project data to send
    project_data = {
        "project_name": "Test Project"
    }
    
    # Send request to create project
    response = await client.post("/api/v1/projects", json=project_data)
    
    # Validate response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "project_id" in data
    assert "created_at" in data
    assert data["project_name"] == "Test Project"
    assert data["user_id"] == str(user.user_id)
    assert uuid.UUID(data["project_id"]) is not None


@pytest.mark.asyncio
async def test_list_projects(authenticated_client, db_session: AsyncSession):
    """Test listing all projects for a user."""
    client, user = authenticated_client
    
    # Create a few projects for the user
    project_names = ["Project 1", "Project 2", "Project 3"]
    projects = []
    
    for name in project_names:
        project = Project(
            project_name=name,
            user_id=user.user_id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        projects.append(project)
    
    await db_session.commit()
    
    # Send request to list projects
    response = await client.get("/api/v1/projects")
    
    # Validate response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(project_names)
    
    # Verify project names match
    received_names = [project["project_name"] for project in data]
    assert sorted(received_names) == sorted(project_names)


@pytest.mark.asyncio
async def test_get_project(authenticated_client, db_session: AsyncSession):
    """Test getting a specific project."""
    client, user = authenticated_client
    
    # Create a project
    project_name = "Project to Get"
    project = Project(
        project_name=project_name,
        user_id=user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Send request to get the project
    response = await client.get(f"/api/v1/projects/{project.project_id}")
    
    # Validate response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["project_name"] == project_name
    assert data["project_id"] == str(project.project_id)
    assert data["user_id"] == str(user.user_id)


@pytest.mark.asyncio
async def test_update_project(authenticated_client, db_session: AsyncSession):
    """Test updating a project."""
    client, user = authenticated_client
    
    # Create a project
    project_name = "Project to Update"
    project = Project(
        project_name=project_name,
        user_id=user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Update data
    update_data = {
        "project_name": "Updated Project Name"
    }
    
    # Send request to update the project
    response = await client.patch(f"/api/v1/projects/{project.project_id}", json=update_data)
    
    # Validate response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["project_name"] == "Updated Project Name"
    assert data["project_id"] == str(project.project_id)
    
    # Verify database was updated
    await db_session.refresh(project)
    assert project.project_name == "Updated Project Name"


@pytest.mark.asyncio
async def test_delete_project(authenticated_client, db_session: AsyncSession):
    """Test deleting a project."""
    client, user = authenticated_client
    
    # Create a project
    project_name = "Project to Delete"
    project = Project(
        project_name=project_name,
        user_id=user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Send request to delete the project
    response = await client.delete(f"/api/v1/projects/{project.project_id}")
    
    # Validate response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify project is deleted
    from src.projects.service import get_project
    with pytest.raises(Exception):  # Should raise ProjectNotFoundException
        await get_project(db_session, user.user_id, project.project_id)
