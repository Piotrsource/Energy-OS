# =============================================================================
# api/v1/energy_meters.py — Energy Meter Router
# =============================================================================
# PURPOSE: Handle energy meter data ingestion (from smart meters/gateways) and
# retrieval (for dashboards and detailed meter inspection).
#
# NOTE: For aggregated analytics (energy summary, carbon emissions), see the
# analytics router. This router handles raw meter data CRUD.
#
# ENDPOINTS:
#   POST /api/v1/energy-meters/readings
#       → Bulk insert energy meter readings (from smart meters)
#   GET  /api/v1/energy-meters/readings?building_id=&meter_id=&start=&end=
#       → Query historical energy meter data with filters
#
# ACCESS CONTROL:
#   - POST: Any authenticated user (meters use service accounts)
#   - GET:  Any authenticated user
# =============================================================================

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.energy_meter import EnergyMeterCreate, EnergyMeterRead
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.energy_meter_service import EnergyMeterService

router = APIRouter()


@router.post(
    "/readings",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert energy meter readings (bulk)",
)
async def insert_meter_readings(
    readings: list[EnergyMeterCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await EnergyMeterService.bulk_insert(db, readings)
    return MessageResponse(message=f"Inserted {count} energy meter readings")


@router.get(
    "/readings",
    response_model=PaginatedResponse[EnergyMeterRead],
    summary="Query energy meter readings",
)
async def query_meter_readings(
    building_id: UUID = Query(..., description="Building to query (required)"),
    meter_id: str | None = Query(None, description="Filter by specific meter ID"),
    start: datetime | None = Query(None, description="Start of time range"),
    end: datetime | None = Query(None, description="End of time range"),
    offset: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await EnergyMeterService.query_readings(
        db,
        building_id=building_id,
        meter_id=meter_id,
        start=start,
        end=end,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(
        items=[EnergyMeterRead.model_validate(m, from_attributes=True) for m in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )
