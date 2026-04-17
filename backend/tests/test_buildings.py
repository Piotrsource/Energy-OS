"""Tests for building CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_buildings(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/buildings", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # PaginatedResponse format
    assert "items" in data
    assert "total_count" in data
    assert isinstance(data["items"], list)
    # admin_user fixture creates one building
    assert data["total_count"] >= 1


@pytest.mark.asyncio
async def test_create_building(client: AsyncClient, auth_headers: dict):
    payload = {
        "name": "New Test Hotel",
        "address": "456 New St",
        "type": "hotel",
        "timezone": "America/New_York",
    }
    response = await client.post(
        "/api/v1/buildings", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Test Hotel"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_building(client: AsyncClient, auth_headers: dict, admin_user):
    building_id = str(admin_user.building_id)
    response = await client.get(
        f"/api/v1/buildings/{building_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == building_id


@pytest.mark.asyncio
async def test_get_nonexistent_building(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/buildings/00000000-0000-0000-0000-000000000099",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_building(client: AsyncClient, auth_headers: dict, admin_user):
    building_id = str(admin_user.building_id)
    response = await client.patch(
        f"/api/v1/buildings/{building_id}",
        json={"name": "Updated Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_building(client: AsyncClient, auth_headers: dict):
    # Create a building to delete
    create_resp = await client.post(
        "/api/v1/buildings",
        json={"name": "To Delete", "address": "nowhere", "type": "office", "timezone": "UTC"},
        headers=auth_headers,
    )
    building_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/buildings/{building_id}", headers=auth_headers
    )
    assert response.status_code == 200

    # Verify it's gone
    get_resp = await client.get(
        f"/api/v1/buildings/{building_id}", headers=auth_headers
    )
    assert get_resp.status_code == 404
