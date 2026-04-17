# =============================================================================
# api/v1/sensors.py — Sensor Data Router
# =============================================================================
# PURPOSE: Handle sensor reading ingestion (from IoT gateways) and
# retrieval (for dashboards and analytics).
#
# This is the highest-throughput endpoint in the system:
#   - Ingestion: ~200-300 writes/second across all buildings
#   - Queries: Time-range filtered reads with TimescaleDB optimization
#
# ENDPOINTS:
#   POST /api/v1/sensors/readings
#       → Bulk insert sensor readings (from IoT gateways)
#   GET  /api/v1/sensors/readings?building_id=&zone_id=&start=&end=
#       → Query historical sensor data with filters
#
# ACCESS CONTROL:
#   - POST: Any authenticated user (sensors/gateways use service accounts)
#   - GET:  Any authenticated user
# =============================================================================

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.sensor import SensorReadingCreate, SensorReadingRead
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.sensor_service import SensorService

router = APIRouter()


@router.post(
    "/readings",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert sensor readings (bulk)",
)
async def insert_readings(
    readings: list[SensorReadingCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await SensorService.bulk_insert(db, readings)
    return MessageResponse(message=f"Inserted {count} sensor readings")


@router.get(
    "/readings",
    response_model=PaginatedResponse[SensorReadingRead],
    summary="Query sensor readings",
)
async def query_readings(
    building_id: UUID = Query(..., description="Building to query (required)"),
    zone_id: UUID | None = Query(None, description="Filter by zone"),
    sensor_type: str | None = Query(None, description="Filter by sensor type"),
    start: datetime | None = Query(None, description="Start of time range (ISO 8601)"),
    end: datetime | None = Query(None, description="End of time range (ISO 8601)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=500, description="Max results (default 500)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await SensorService.query_readings(
        db,
        building_id=building_id,
        zone_id=zone_id,
        sensor_type=sensor_type,
        start=start,
        end=end,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(
        items=[SensorReadingRead.model_validate(r, from_attributes=True) for r in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )
