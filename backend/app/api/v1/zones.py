# =============================================================================
# api/v1/zones.py — Zone CRUD Router
# =============================================================================
# PURPOSE: Handle HTTP requests for zone management.
# Zones represent distinct areas within buildings (floors, wings, rooms)
# and are the granularity at which AI forecasts and recommendations operate.
#
# ENDPOINTS:
#   GET  /api/v1/zones?building_id=  → List zones for a building
#   POST /api/v1/zones               → Create a new zone
#   GET  /api/v1/zones/{id}          → Get a specific zone
#
# ACCESS CONTROL:
#   - GET:   Any authenticated user
#   - POST:  Admin or Facility Manager
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.zone import ZoneCreate, ZoneRead
from app.schemas.common import PaginatedResponse
from app.services.zone_service import ZoneService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[ZoneRead],
    summary="List zones for a building",
)
async def list_zones(
    building_id: UUID = Query(..., description="Filter zones by building ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await ZoneService.list_by_building(
        db, building_id, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=[ZoneRead.model_validate(z, from_attributes=True) for z in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )


# =============================================================================
# CREATE A ZONE
# =============================================================================
@router.post(
    "/",
    response_model=ZoneRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new zone",
)
async def create_zone(
    payload: ZoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)
    ),
):
    """
    Create a new zone within a building.
    The building_id in the request body must reference an existing building.
    Requires admin or facility_manager role.
    """
    return await ZoneService.create(db, payload)


# =============================================================================
# GET A SINGLE ZONE
# =============================================================================
@router.get(
    "/{zone_id}",
    response_model=ZoneRead,
    summary="Get a zone by ID",
)
async def get_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific zone by its UUID.
    Returns 404 if the zone does not exist.
    """
    zone = await ZoneService.get_by_id(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )
    return zone
