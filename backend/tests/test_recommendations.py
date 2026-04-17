"""Tests for recommendation endpoints (CRUD + lifecycle)."""

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.zone import Zone


@pytest.mark.asyncio
async def test_create_recommendation(
    client: AsyncClient,
    auth_headers: dict,
    test_zone: Zone,
):
    payload = {
        "zone_id": str(test_zone.id),
        "recommendation_type": "hvac_setpoint",
        "value": 22.5,
    }
    response = await client.post(
        "/api/v1/recommendations", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["zone_id"] == str(test_zone.id)
    assert data["recommendation_type"] == "hvac_setpoint"
    assert data["value"] == 22.5
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_recommendations(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
    test_zone: Zone,
):
    # Create a recommendation first
    payload = {
        "zone_id": str(test_zone.id),
        "recommendation_type": "lighting_level",
        "value": 75.0,
    }
    await client.post("/api/v1/recommendations", json=payload, headers=auth_headers)

    # List
    response = await client.get(
        f"/api/v1/recommendations?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] >= 1


@pytest.mark.asyncio
async def test_update_recommendation_approve(
    client: AsyncClient,
    auth_headers: dict,
    test_zone: Zone,
):
    # Create
    create_resp = await client.post(
        "/api/v1/recommendations",
        json={
            "zone_id": str(test_zone.id),
            "recommendation_type": "hvac_setpoint",
            "value": 21.0,
        },
        headers=auth_headers,
    )
    rec_id = create_resp.json()["id"]

    # Approve
    response = await client.patch(
        f"/api/v1/recommendations/{rec_id}",
        json={"status": "approved"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_update_recommendation_apply(
    client: AsyncClient,
    auth_headers: dict,
    test_zone: Zone,
):
    # Create
    create_resp = await client.post(
        "/api/v1/recommendations",
        json={
            "zone_id": str(test_zone.id),
            "recommendation_type": "ventilation_rate",
            "value": 500.0,
        },
        headers=auth_headers,
    )
    rec_id = create_resp.json()["id"]

    # Apply — applied_at should be auto-set
    response = await client.patch(
        f"/api/v1/recommendations/{rec_id}",
        json={"status": "applied"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "applied"
    assert data["applied_at"] is not None


@pytest.mark.asyncio
async def test_update_recommendation_reject(
    client: AsyncClient,
    auth_headers: dict,
    test_zone: Zone,
):
    # Create
    create_resp = await client.post(
        "/api/v1/recommendations",
        json={
            "zone_id": str(test_zone.id),
            "recommendation_type": "hvac_schedule",
            "value": 18.0,
        },
        headers=auth_headers,
    )
    rec_id = create_resp.json()["id"]

    # Reject
    response = await client.patch(
        f"/api/v1/recommendations/{rec_id}",
        json={"status": "rejected"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_update_recommendation_invalid_status(
    client: AsyncClient,
    auth_headers: dict,
    test_zone: Zone,
):
    # Create
    create_resp = await client.post(
        "/api/v1/recommendations",
        json={
            "zone_id": str(test_zone.id),
            "recommendation_type": "hvac_setpoint",
            "value": 22.0,
        },
        headers=auth_headers,
    )
    rec_id = create_resp.json()["id"]

    # Invalid status
    response = await client.patch(
        f"/api/v1/recommendations/{rec_id}",
        json={"status": "invalid_status"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_nonexistent_recommendation(
    client: AsyncClient,
    auth_headers: dict,
):
    response = await client.patch(
        "/api/v1/recommendations/00000000-0000-0000-0000-000000000099",
        json={"status": "approved"},
        headers=auth_headers,
    )
    assert response.status_code == 404
