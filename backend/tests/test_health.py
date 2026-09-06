import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Verify that root endpoint responds with operational status."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ORBIT Geospatial Intelligence"
    assert data["status"] == "operational"
    assert data["health"] == "/api/v1/health"


@pytest.mark.asyncio
async def test_health_endpoint_structure(async_client: AsyncClient):
    """Verify that the health check endpoint returns the standardized structure."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "timestamp_utc" in data
    assert "environment" in data
    assert "services" in data
    assert "api" in data["services"]
    assert data["services"]["api"]["status"] == "healthy"
    assert "database" in data["services"]
    assert "postgis" in data["services"]
    assert "redis" in data["services"]
