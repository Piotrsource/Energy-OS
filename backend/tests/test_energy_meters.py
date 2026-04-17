"""Tests for energy meter endpoints."""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_insert_meter_readings(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    readings = [
        {
            "time": datetime.utcnow().isoformat(),
            "meter_id": "meter-001",
            "building_id": str(admin_user.building_id),
            "kwh": 150.5,
            "voltage": 230.0,
            "current": 12.3,
        }
    ]
    response = await client.post(
        "/api/v1/energy-meters/readings", json=readings, headers=auth_headers
    )
    assert response.status_code == 201
    assert "1 energy" in response.json()["message"]


@pytest.mark.asyncio
async def test_insert_meter_readings_bulk(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    readings = [
        {
            "time": datetime.utcnow().isoformat(),
            "meter_id": f"meter-{i:03d}",
            "building_id": str(admin_user.building_id),
            "kwh": 100.0 + i * 10,
        }
        for i in range(5)
    ]
    response = await client.post(
        "/api/v1/energy-meters/readings", json=readings, headers=auth_headers
    )
    assert response.status_code == 201
    assert "5 energy" in response.json()["message"]


@pytest.mark.asyncio
async def test_query_meter_readings(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    # Insert data first
    readings = [
        {
            "time": datetime.utcnow().isoformat(),
            "meter_id": "meter-query-001",
            "building_id": str(admin_user.building_id),
            "kwh": 200.0,
            "voltage": 240.0,
            "current": 15.0,
        }
    ]
    await client.post(
        "/api/v1/energy-meters/readings", json=readings, headers=auth_headers
    )

    # Query
    response = await client.get(
        f"/api/v1/energy-meters/readings?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] >= 1


@pytest.mark.asyncio
async def test_query_meter_readings_empty(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    response = await client.get(
        f"/api/v1/energy-meters/readings?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_count"] == 0
