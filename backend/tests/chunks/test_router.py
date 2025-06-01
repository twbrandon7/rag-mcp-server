"""Tests for chunk-related endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import URL, Project, User, Chunk


@pytest.fixture
async def authenticated_client_with_data(client: AsyncClient, db_session):
    """Fixture for a client with authenticated user, project, URL, and chunks"""
    # Create a test user
    user_id = uuid.uuid4()
    user = User(
        user_id=user_id,
        email="test_chunks@example.com",
        password_hash="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create a test project
    project_id = uuid.uuid4()
    project = Project(
        project_id=project_id,
        user_id=user_id,
        project_name="Test Project for Chunks",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(project)
    
    # Create a test URL
    url_id = uuid.uuid4()
    url = URL(
        url_id=url_id,
        project_id=project_id,
        original_url="https://example.com/test",
        status="stored",
        submitted_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc)
    )
    db_session.add(url)
    
    # Create test chunks
    # Use 384-dimensional embeddings to match the Vector field configuration
    embedding1 = [0.1] * 384  # 384 elements all set to 0.1
    embedding2 = [0.2] * 384  # 384 elements all set to 0.2
    
    chunk1 = Chunk(
        chunk_id=uuid.uuid4(),
        url_id=url_id,
        project_id=project_id,
        content="This is the first chunk of content from the webpage.",
        chunk_index=0,
        embedding=embedding1,
        created_at=datetime.now(timezone.utc)
    )
    chunk2 = Chunk(
        chunk_id=uuid.uuid4(),
        url_id=url_id,
        project_id=project_id,
        content="This is the second chunk of content from the webpage.",
        chunk_index=1,
        embedding=embedding2,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(chunk1)
    db_session.add(chunk2)
    await db_session.commit()
    
    # Mock token creation
    token = "test_access_token_for_chunks"
    with patch("src.auth.dependencies.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": str(user_id)}
        
        # Return configured client
        client.headers["Authorization"] = f"Bearer {token}"
        yield client, user, project, url, [chunk1, chunk2]


async def test_get_content_chunks_without_vectors(authenticated_client_with_data):
    """Test getting content chunks without vector embeddings."""
    client, user, project, url, chunks = authenticated_client_with_data
    
    response = await client.get(
        f"/api/v1/projects/{project.project_id}/urls/{url.url_id}/chunks"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data) == 2
    assert data[0]["content"] == "This is the first chunk of content from the webpage."
    assert data[1]["content"] == "This is the second chunk of content from the webpage."
    assert data[0]["chunk_index"] == 0
    assert data[1]["chunk_index"] == 1
    # Embeddings should not be included
    assert data[0]["embedding"] is None
    assert data[1]["embedding"] is None


async def test_get_content_chunks_with_vectors(authenticated_client_with_data):
    """Test getting content chunks with vector embeddings."""
    client, user, project, url, chunks = authenticated_client_with_data
    
    response = await client.get(
        f"/api/v1/projects/{project.project_id}/urls/{url.url_id}/chunks?include_vectors=true"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data) == 2
    # Embeddings should be included
    assert len(data[0]["embedding"]) == 384
    assert len(data[1]["embedding"]) == 384
    # Check that embeddings are approximately the expected values
    assert all(abs(val - 0.1) < 0.001 for val in data[0]["embedding"])
    assert all(abs(val - 0.2) < 0.001 for val in data[1]["embedding"])


async def test_get_content_chunks_url_not_found(authenticated_client_with_data):
    """Test getting chunks for a non-existent URL."""
    client, user, project, url, chunks = authenticated_client_with_data
    
    fake_url_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/projects/{project.project_id}/urls/{fake_url_id}/chunks"
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_query_content_chunks(authenticated_client_with_data):
    """Test querying content chunks (placeholder implementation)."""
    client, user, project, url, chunks = authenticated_client_with_data
    
    query_data = {
        "query": "test query",
        "top_k": 2
    }
    
    response = await client.post(
        f"/api/v1/projects/{project.project_id}/urls/{url.url_id}/chunks:query",
        json=query_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "results" in data
    assert len(data["results"]) <= 2  # Should return at most top_k results
    
    # Check result structure
    if data["results"]:
        result = data["results"][0]
        assert "chunk_id" in result
        assert "content" in result
        assert "similarity_score" in result
        assert "chunk_index" in result
        assert "created_at" in result


async def test_query_content_chunks_invalid_query(authenticated_client_with_data):
    """Test querying with invalid parameters."""
    client, user, project, url, chunks = authenticated_client_with_data
    
    # Test empty query
    query_data = {
        "query": "",
        "top_k": 5
    }
    
    response = await client.post(
        f"/api/v1/projects/{project.project_id}/urls/{url.url_id}/chunks:query",
        json=query_data
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test top_k too large
    query_data = {
        "query": "test query",
        "top_k": 100  # Above the maximum limit of 50
    }
    
    response = await client.post(
        f"/api/v1/projects/{project.project_id}/urls/{url.url_id}/chunks:query",
        json=query_data
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_query_content_chunks_url_not_found(authenticated_client_with_data):
    """Test querying chunks for a non-existent URL."""
    client, user, project, url, chunks = authenticated_client_with_data
    
    fake_url_id = uuid.uuid4()
    query_data = {
        "query": "test query",
        "top_k": 5
    }
    
    response = await client.post(
        f"/api/v1/projects/{fake_url_id}/urls/{fake_url_id}/chunks:query",
        json=query_data
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
