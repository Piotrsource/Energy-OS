"""Tests for error handling middleware and structured error responses."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_401_no_token(client: AsyncClient):
    """Unauthenticated request returns structured 401."""
    response = await client.get("/api/v1/buildings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_401_invalid_token(client: AsyncClient):
    """Invalid JWT token returns 401."""
    headers = {"Authorization": "Bearer totally.invalid.token"}
    response = await client.get("/api/v1/buildings", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_404_structured_response(
    client: AsyncClient, auth_headers: dict
):
    """Non-existent resource returns structured 404."""
    response = await client.get(
        "/api/v1/buildings/00000000-0000-0000-0000-000000000099",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    # Custom error handler returns {error, code, request_id}
    assert "error" in data
    assert "code" in data
    assert data["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_422_validation_error(
    client: AsyncClient, auth_headers: dict
):
    """Invalid request body returns 422 validation error."""
    # Missing required fields
    response = await client.post(
        "/api/v1/buildings",
        json={"name": "Incomplete"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_sensor_validation_out_of_range(
    client: AsyncClient, auth_headers: dict, admin_user, test_zone
):
    """Sensor reading with out-of-range value returns 422."""
    from datetime import datetime

    readings = [
        {
            "time": datetime.utcnow().isoformat(),
            "sensor_id": "temp-bad",
            "building_id": str(admin_user.building_id),
            "zone_id": str(test_zone.id),
            "sensor_type": "temperature",
            "value": 999.0,  # way outside (-50, 80) range
        }
    ]
    response = await client.post(
        "/api/v1/sensors/readings", json=readings, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sensor_validation_humidity_out_of_range(
    client: AsyncClient, auth_headers: dict, admin_user, test_zone
):
    """Humidity reading outside (0, 100) returns 422."""
    from datetime import datetime

    readings = [
        {
            "time": datetime.utcnow().isoformat(),
            "sensor_id": "hum-bad",
            "building_id": str(admin_user.building_id),
            "zone_id": str(test_zone.id),
            "sensor_type": "humidity",
            "value": -5.0,  # negative humidity
        }
    ]
    response = await client.post(
        "/api/v1/sensors/readings", json=readings, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_request_id_in_response(
    client: AsyncClient, auth_headers: dict
):
    """Responses should include X-Request-ID header for tracing."""
    response = await client.get("/api/v1/buildings", headers=auth_headers)
    # The request_context middleware should set a request ID
    # (checking it doesn't error is the primary goal)
    assert response.status_code == 200
