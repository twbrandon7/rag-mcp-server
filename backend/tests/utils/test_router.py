import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/api/v1/utils/health-check/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == True
