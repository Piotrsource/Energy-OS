"""Tests for role-based access control (RBAC).

Verifies that technicians (lowest privilege) are correctly denied
access to admin/facility_manager-only endpoints, while retaining
read access and the ability to update recommendation status.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.zone import Zone


# ── TECHNICIAN DENIED: building write operations ─────────────────────────


@pytest.mark.asyncio
async def test_technician_cannot_create_building(
    client: AsyncClient, technician_headers: dict
):
    """POST /buildings requires admin or facility_manager role."""
    response = await client.post(
        "/api/v1/buildings",
        json={
            "name": "Unauthorized Hotel",
            "address": "Nowhere",
            "type": "hotel",
            "timezone": "UTC",
        },
        headers=technician_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_technician_cannot_update_building(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """PATCH /buildings/{id} requires admin or facility_manager role."""
    response = await client.patch(
        f"/api/v1/buildings/{admin_user.building_id}",
        json={"name": "Hacked Name"},
        headers=technician_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_technician_cannot_delete_building(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """DELETE /buildings/{id} requires admin or facility_manager role."""
    response = await client.delete(
        f"/api/v1/buildings/{admin_user.building_id}",
        headers=technician_headers,
    )
    assert response.status_code == 403


# ── TECHNICIAN DENIED: zone write operations ─────────────────────────────


@pytest.mark.asyncio
async def test_technician_cannot_create_zone(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """POST /zones requires admin or facility_manager role."""
    response = await client.post(
        "/api/v1/zones",
        json={
            "building_id": str(admin_user.building_id),
            "name": "Unauthorized Zone",
            "floor": 99,
        },
        headers=technician_headers,
    )
    assert response.status_code == 403


# ── TECHNICIAN DENIED: forecast creation ─────────────────────────────────


@pytest.mark.asyncio
async def test_technician_cannot_create_forecast(
    client: AsyncClient,
    technician_headers: dict,
    test_zone: Zone,
):
    """POST /forecasts requires admin or facility_manager role."""
    from datetime import datetime, timezone, timedelta

    response = await client.post(
        "/api/v1/forecasts",
        json={
            "zone_id": str(test_zone.id),
            "forecast_type": "energy_demand",
            "predicted_value": 100.0,
            "forecast_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        },
        headers=technician_headers,
    )
    assert response.status_code == 403


# ── TECHNICIAN DENIED: recommendation creation ──────────────────────────


@pytest.mark.asyncio
async def test_technician_cannot_create_recommendation(
    client: AsyncClient,
    technician_headers: dict,
    test_zone: Zone,
):
    """POST /recommendations requires admin or facility_manager role."""
    response = await client.post(
        "/api/v1/recommendations",
        json={
            "zone_id": str(test_zone.id),
            "recommendation_type": "hvac_setpoint",
            "value": 20.0,
        },
        headers=technician_headers,
    )
    assert response.status_code == 403


# ── TECHNICIAN ALLOWED: read operations ──────────────────────────────────


@pytest.mark.asyncio
async def test_technician_can_list_buildings(
    client: AsyncClient, technician_headers: dict
):
    """GET /buildings is allowed for any authenticated user."""
    response = await client.get("/api/v1/buildings", headers=technician_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_technician_can_list_zones(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """GET /zones is allowed for any authenticated user."""
    response = await client.get(
        f"/api/v1/zones?building_id={admin_user.building_id}",
        headers=technician_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_technician_can_list_forecasts(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """GET /forecasts is allowed for any authenticated user."""
    response = await client.get(
        f"/api/v1/forecasts?building_id={admin_user.building_id}",
        headers=technician_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_technician_can_query_sensors(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """GET /sensors/readings is allowed for any authenticated user."""
    response = await client.get(
        f"/api/v1/sensors/readings?building_id={admin_user.building_id}",
        headers=technician_headers,
    )
    assert response.status_code == 200


# ── TECHNICIAN ALLOWED: recommendation status updates ────────────────────


@pytest.mark.asyncio
async def test_technician_can_update_recommendation_status(
    client: AsyncClient,
    auth_headers: dict,
    technician_headers: dict,
    test_zone: Zone,
):
    """PATCH /recommendations/{id} is allowed for technicians."""
    # Admin creates a recommendation
    create_resp = await client.post(
        "/api/v1/recommendations",
        json={
            "zone_id": str(test_zone.id),
            "recommendation_type": "hvac_setpoint",
            "value": 23.0,
        },
        headers=auth_headers,
    )
    rec_id = create_resp.json()["id"]

    # Technician updates its status
    response = await client.patch(
        f"/api/v1/recommendations/{rec_id}",
        json={"status": "approved"},
        headers=technician_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


# ── USER MANAGEMENT: admin only ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_technician_cannot_list_users(
    client: AsyncClient, technician_headers: dict
):
    """GET /users requires admin role."""
    response = await client.get("/api/v1/users", headers=technician_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_technician_cannot_create_user(
    client: AsyncClient,
    technician_headers: dict,
    admin_user: User,
):
    """POST /users requires admin role."""
    response = await client.post(
        "/api/v1/users",
        json={
            "building_id": str(admin_user.building_id),
            "name": "New User",
            "email": "newuser@test.local",
            "role": "technician",
            "password": "securepass123",
        },
        headers=technician_headers,
    )
    assert response.status_code == 403
