"""Tests for the health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Health endpoint returns status, db, and version fields
    assert "status" in data
    assert data["status"] in ("ok", "degraded")
    assert "version" in data
