# =============================================================================
# api/v1/hvac.py — HVAC Status Router
# =============================================================================
# PURPOSE: Handle HVAC status ingestion (from BMS/HVAC controllers) and
# retrieval (for dashboards and equipment monitoring).
#
# ENDPOINTS:
#   POST /api/v1/hvac/status
#       → Bulk insert HVAC status snapshots (from BMS controllers)
#   GET  /api/v1/hvac/status?building_id=&zone_id=&device_type=&start=&end=
#       → Query historical HVAC status data with filters
#
# ACCESS CONTROL:
#   - POST: Any authenticated user (BMS systems use service accounts)
#   - GET:  Any authenticated user
# =============================================================================

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.hvac import HvacStatusCreate, HvacStatusRead
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.hvac_service import HvacService

router = APIRouter()


@router.post(
    "/status",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert HVAC status snapshots (bulk)",
)
async def insert_hvac_status(
    entries: list[HvacStatusCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await HvacService.bulk_insert(db, entries)
    return MessageResponse(message=f"Inserted {count} HVAC status entries")


@router.get(
    "/status",
    response_model=PaginatedResponse[HvacStatusRead],
    summary="Query HVAC status history",
)
async def query_hvac_status(
    building_id: UUID = Query(..., description="Building to query (required)"),
    zone_id: UUID | None = Query(None, description="Filter by zone"),
    device_type: str | None = Query(None, description="Filter by device type"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    start: datetime | None = Query(None, description="Start of time range"),
    end: datetime | None = Query(None, description="End of time range"),
    offset: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await HvacService.query_status(
        db,
        building_id=building_id,
        zone_id=zone_id,
        device_type=device_type,
        status_filter=status_filter,
        start=start,
        end=end,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(
        items=[HvacStatusRead.model_validate(h, from_attributes=True) for h in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )
