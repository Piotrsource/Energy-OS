"""Tests for pagination behavior across list endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_pagination_response_structure(
    client: AsyncClient, auth_headers: dict
):
    """All paginated endpoints return items, total_count, offset, limit."""
    response = await client.get("/api/v1/buildings", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert "offset" in data
    assert "limit" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total_count"], int)
    assert isinstance(data["offset"], int)
    assert isinstance(data["limit"], int)


@pytest.mark.asyncio
async def test_pagination_default_values(
    client: AsyncClient, auth_headers: dict
):
    """Default offset=0 and limit should be applied."""
    response = await client.get("/api/v1/buildings", headers=auth_headers)
    data = response.json()
    assert data["offset"] == 0
    assert data["limit"] > 0  # default limit is set


@pytest.mark.asyncio
async def test_pagination_custom_offset_limit(
    client: AsyncClient, auth_headers: dict
):
    """Custom offset and limit are respected."""
    # Create several buildings
    for i in range(5):
        await client.post(
            "/api/v1/buildings",
            json={
                "name": f"Paginated Building {i}",
                "address": f"{i} Test Ave",
                "type": "hotel",
                "timezone": "UTC",
            },
            headers=auth_headers,
        )

    # Request with small limit
    response = await client.get(
        "/api/v1/buildings?offset=0&limit=2", headers=auth_headers
    )
    data = response.json()
    assert data["offset"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) <= 2
    assert data["total_count"] >= 5  # at least the 5 we created


@pytest.mark.asyncio
async def test_pagination_offset_skips_items(
    client: AsyncClient, auth_headers: dict
):
    """Using offset skips the first N items."""
    # Create buildings
    for i in range(3):
        await client.post(
            "/api/v1/buildings",
            json={
                "name": f"Offset Building {i}",
                "address": f"{i} Skip St",
                "type": "office",
                "timezone": "UTC",
            },
            headers=auth_headers,
        )

    # Get all
    all_resp = await client.get(
        "/api/v1/buildings?offset=0&limit=100", headers=auth_headers
    )
    all_data = all_resp.json()
    total = all_data["total_count"]

    # Get with offset = 1
    offset_resp = await client.get(
        "/api/v1/buildings?offset=1&limit=100", headers=auth_headers
    )
    offset_data = offset_resp.json()
    # Should have one less item
    assert len(offset_data["items"]) == total - 1


@pytest.mark.asyncio
async def test_pagination_zones(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Zone list endpoint also returns PaginatedResponse."""
    building_id = str(admin_user.building_id)

    # Create zones
    for i in range(3):
        await client.post(
            "/api/v1/zones",
            json={"building_id": building_id, "name": f"Zone {i}", "floor": i},
            headers=auth_headers,
        )

    response = await client.get(
        f"/api/v1/zones?building_id={building_id}&offset=0&limit=2",
        headers=auth_headers,
    )
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] >= 3
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_pagination_sensor_readings(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Sensor readings endpoint supports pagination."""
    response = await client.get(
        f"/api/v1/sensors/readings?building_id={admin_user.building_id}"
        f"&offset=0&limit=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["limit"] == 10
