"""Tests for zone CRUD endpoints."""

import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
async def test_create_zone(client: AsyncClient, auth_headers: dict, admin_user: User):
    payload = {
        "building_id": str(admin_user.building_id),
        "name": "Test Zone Floor 1",
        "floor": 1,
    }
    response = await client.post(
        "/api/v1/zones", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Zone Floor 1"
    assert data["floor"] == 1


@pytest.mark.asyncio
async def test_list_zones(client: AsyncClient, auth_headers: dict, admin_user: User):
    building_id = str(admin_user.building_id)

    # Create a zone first
    await client.post(
        "/api/v1/zones",
        json={"building_id": building_id, "name": "Lobby", "floor": 1},
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/v1/zones?building_id={building_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # PaginatedResponse format
    assert "items" in data
    assert "total_count" in data
    assert isinstance(data["items"], list)
    assert data["total_count"] >= 1
