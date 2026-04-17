"""Tests for HVAC status endpoints."""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.zone import Zone


@pytest.mark.asyncio
async def test_insert_hvac_status(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
    test_zone: Zone,
):
    entries = [
        {
            "time": datetime.utcnow().isoformat(),
            "device_id": "ahu-001",
            "building_id": str(admin_user.building_id),
            "zone_id": str(test_zone.id),
            "device_type": "ahu",
            "status": "running",
            "setpoint": 22.0,
        }
    ]
    response = await client.post(
        "/api/v1/hvac/status", json=entries, headers=auth_headers
    )
    assert response.status_code == 201
    assert "1 HVAC" in response.json()["message"]


@pytest.mark.asyncio
async def test_insert_hvac_multiple(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
    test_zone: Zone,
):
    entries = [
        {
            "time": datetime.utcnow().isoformat(),
            "device_id": f"ahu-{i:03d}",
            "building_id": str(admin_user.building_id),
            "zone_id": str(test_zone.id),
            "device_type": "ahu",
            "status": "running",
            "setpoint": 21.0 + i,
        }
        for i in range(3)
    ]
    response = await client.post(
        "/api/v1/hvac/status", json=entries, headers=auth_headers
    )
    assert response.status_code == 201
    assert "3 HVAC" in response.json()["message"]


@pytest.mark.asyncio
async def test_query_hvac_status(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
    test_zone: Zone,
):
    # Insert data first
    entries = [
        {
            "time": datetime.utcnow().isoformat(),
            "device_id": "chiller-001",
            "building_id": str(admin_user.building_id),
            "zone_id": str(test_zone.id),
            "device_type": "chiller",
            "status": "idle",
            "setpoint": None,
        }
    ]
    await client.post("/api/v1/hvac/status", json=entries, headers=auth_headers)

    # Query
    response = await client.get(
        f"/api/v1/hvac/status?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] >= 1
    assert data["items"][0]["device_type"] == "chiller"


@pytest.mark.asyncio
async def test_query_hvac_empty(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    response = await client.get(
        f"/api/v1/hvac/status?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_count"] == 0
