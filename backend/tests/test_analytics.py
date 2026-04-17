"""Tests for analytics endpoints (energy summary, carbon, anomalies)."""

from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient

from app.models.user import User


def _time_range() -> tuple[str, str]:
    """Return ISO 8601 start/end strings (naive UTC — no tz suffix).

    The energy_meter model uses TIMESTAMP WITHOUT TIME ZONE,
    so we must send naive datetime strings to avoid asyncpg's
    'offset-naive vs offset-aware' mismatch.
    """
    now = datetime.utcnow()
    start = (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    end = now.strftime("%Y-%m-%dT%H:%M:%S")
    return start, end


@pytest.mark.asyncio
async def test_energy_summary_empty(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Energy summary with no data returns valid structure."""
    start, end = _time_range()

    response = await client.get(
        f"/api/v1/buildings/{admin_user.building_id}/energy-summary",
        params={"start": start, "end": end},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "building_id" in data
    assert "buckets" in data
    assert "total_kwh" in data


@pytest.mark.asyncio
async def test_energy_summary_with_data(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Energy summary with meter data returns aggregated buckets."""
    now = datetime.utcnow()

    # Insert energy meter readings
    readings = [
        {
            "time": (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S"),
            "meter_id": "meter-analytics-001",
            "building_id": str(admin_user.building_id),
            "kwh": 50.0 + i * 10,
        }
        for i in range(3)
    ]
    await client.post(
        "/api/v1/energy-meters/readings", json=readings, headers=auth_headers
    )

    start, end = _time_range()
    response = await client.get(
        f"/api/v1/buildings/{admin_user.building_id}/energy-summary",
        params={"start": start, "end": end},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_kwh"] >= 0


@pytest.mark.asyncio
async def test_carbon_emissions(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Carbon emissions endpoint returns valid structure."""
    start, end = _time_range()

    response = await client.get(
        f"/api/v1/buildings/{admin_user.building_id}/carbon-emissions",
        params={"start": start, "end": end},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "building_id" in data
    assert "emission_factor_kg_per_kwh" in data
    assert "total_carbon_kg" in data
    assert "buckets" in data


@pytest.mark.asyncio
async def test_carbon_emissions_custom_factor(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Carbon emissions with custom emission factor."""
    start, end = _time_range()

    response = await client.get(
        f"/api/v1/buildings/{admin_user.building_id}/carbon-emissions",
        params={"start": start, "end": end, "emission_factor": "0.8"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["emission_factor_kg_per_kwh"] == 0.8


@pytest.mark.asyncio
async def test_anomalies(
    client: AsyncClient,
    auth_headers: dict,
    admin_user: User,
):
    """Anomalies endpoint returns a list (may be empty with no data)."""
    response = await client.get(
        "/api/v1/anomalies",
        params={"building_id": str(admin_user.building_id)},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
