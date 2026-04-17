# =============================================================================
# api/v1/analytics.py — Analytics & Dashboard Router
# =============================================================================
# PURPOSE: Serve aggregated data for the frontend dashboard.
# These endpoints use TimescaleDB's time_bucket() for efficient aggregation
# over large time-series datasets.
#
# ENDPOINTS:
#   GET /api/v1/buildings/{id}/energy-summary?start=&end=
#       → Hourly energy consumption aggregation
#   GET /api/v1/buildings/{id}/carbon-emissions?start=&end=
#       → Estimated CO2 emissions from energy usage
#   GET /api/v1/anomalies?building_id=&start=&end=
#       → Detected anomalies in sensor data
#
# ACCESS CONTROL:
#   All endpoints: Any authenticated user
#
# DATA SOURCE:
#   These endpoints read from TimescaleDB hypertables (energy_meter,
#   sensor_readings) and return aggregated results — they never modify data.
# =============================================================================

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.energy import EnergySummary, CarbonEmissions, AnomalyRecord
from app.services.analytics_service import AnalyticsService

router = APIRouter()


# =============================================================================
# ENERGY SUMMARY
# =============================================================================
@router.get(
    "/buildings/{building_id}/energy-summary",
    response_model=EnergySummary,
    summary="Get energy consumption summary",
)
async def get_energy_summary(
    building_id: UUID,
    start: datetime = Query(..., description="Start of time range (ISO 8601)"),
    end: datetime = Query(..., description="End of time range (ISO 8601)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated energy consumption for a building over a time range.

    Returns hourly buckets with total, average, and peak kWh values.
    Uses TimescaleDB's time_bucket() for efficient aggregation.

    Example: Get yesterday's energy data:
        ?start=2026-03-01T00:00:00Z&end=2026-03-01T23:59:59Z
    """
    return await AnalyticsService.get_energy_summary(db, building_id, start, end)


# =============================================================================
# CARBON EMISSIONS
# =============================================================================
@router.get(
    "/buildings/{building_id}/carbon-emissions",
    response_model=CarbonEmissions,
    summary="Get estimated carbon emissions",
)
async def get_carbon_emissions(
    building_id: UUID,
    start: datetime = Query(..., description="Start of time range (ISO 8601)"),
    end: datetime = Query(..., description="End of time range (ISO 8601)"),
    emission_factor: float = Query(
        0.4,
        description="CO2 emission factor in kg CO2 per kWh (default: 0.4, US grid average)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Estimate CO2 emissions from a building's energy consumption.

    Converts kWh to kg CO2 using the emission factor.
    Default factor (0.4 kg/kWh) is an approximate US grid average.
    Override with your local grid's emission factor for accuracy.
    """
    return await AnalyticsService.get_carbon_emissions(
        db, building_id, start, end, emission_factor
    )


# =============================================================================
# ANOMALIES
# =============================================================================
@router.get(
    "/anomalies",
    response_model=list[AnomalyRecord],
    summary="Get detected anomalies",
)
async def get_anomalies(
    building_id: UUID = Query(..., description="Building to check for anomalies"),
    start: datetime | None = Query(None, description="Start of time range"),
    end: datetime | None = Query(None, description="End of time range"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Detect anomalies in sensor readings for a building.

    Uses a z-score method: readings that deviate more than 3 standard
    deviations from the mean are flagged. Severity is classified as:
    - low:      z-score 3.0 - 3.5
    - medium:   z-score 3.5 - 4.0
    - high:     z-score 4.0 - 5.0
    - critical: z-score > 5.0

    Note: This is a basic statistical method. The AI/ML engine will provide
    more sophisticated anomaly detection in production.
    """
    return await AnalyticsService.get_anomalies(db, building_id, start, end)
