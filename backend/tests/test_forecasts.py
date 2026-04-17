"""Tests for forecast endpoints."""

from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.zone import Zone


@pytest.mark.asyncio
async def test_create_forecast(
    client: AsyncClient,
    auth_headers: dict,
    test_zone: Zone,
):
    payload = {
        "zone_id": str(test_zone.id),
        "forecast_type": "energy_demand",
        "predicted_value": 125.5,
        "forecast_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
    }
    response = await client.post(
        "/api/v1/forecasts", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["zone_id"] == str(test_zone.id)
    assert data["forecast_type"] == "energy_demand"
    assert data["predicted_value"] == 125.5
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_forecasts(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
    test_zone: Zone,
):
    # Create a forecast first
    payload = {
        "zone_id": str(test_zone.id),
        "forecast_type": "occupancy",
        "predicted_value": 42.0,
        "forecast_time": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
    }
    await client.post("/api/v1/forecasts", json=payload, headers=auth_headers)

    # List
    response = await client.get(
        f"/api/v1/forecasts?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] >= 1
    assert data["items"][0]["forecast_type"] in ("energy_demand", "occupancy")


@pytest.mark.asyncio
async def test_list_forecasts_empty(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    response = await client.get(
        f"/api/v1/forecasts?building_id={admin_user.building_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_count"] == 0
