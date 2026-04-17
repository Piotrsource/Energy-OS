"""Tests for sensor data endpoints."""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.zone import Zone


@pytest.mark.asyncio
async def test_insert_sensor_readings(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
    db_session: AsyncSession,
):
    # Create a zone for sensor data
    zone = Zone(
        id=uuid.uuid4(),
        building_id=admin_user.building_id,
        name="Sensor Test Zone",
        floor=1,
    )
    db_session.add(zone)
    await db_session.commit()

    readings = [
        {
            "time": datetime.utcnow().isoformat(),
            "sensor_id": "temp-001",
            "building_id": str(admin_user.building_id),
            "zone_id": str(zone.id),
            "sensor_type": "temperature",
            "value": 22.5,
        }
    ]

    response = await client.post(
        "/api/v1/sensors/readings", json=readings, headers=auth_headers
    )
    assert response.status_code == 201
    assert "1 sensor" in response.json()["message"]


@pytest.mark.asyncio
async def test_query_sensor_readings(
    client: AsyncClient, auth_headers: dict, admin_user: User
):
    building_id = str(admin_user.building_id)
    response = await client.get(
        f"/api/v1/sensors/readings?building_id={building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # PaginatedResponse format
    assert "items" in data
    assert "total_count" in data
    assert isinstance(data["items"], list)
