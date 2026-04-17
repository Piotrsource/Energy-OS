# =============================================================================
# api/v1/buildings.py — Building CRUD Router
# =============================================================================
# PURPOSE: Handle HTTP requests for building management.
# Buildings are the top-level entity — every zone, sensor, and user belongs
# to a building.
#
# ENDPOINTS:
#   GET    /api/v1/buildings          → List all buildings
#   POST   /api/v1/buildings          → Create a new building
#   GET    /api/v1/buildings/{id}     → Get a specific building
#   PATCH  /api/v1/buildings/{id}     → Update a building
#   DELETE /api/v1/buildings/{id}     → Delete a building (cascades to zones)
#
# ACCESS CONTROL:
#   - GET:                Any authenticated user
#   - POST/PATCH/DELETE:  Admin or Facility Manager only
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.building import BuildingCreate, BuildingUpdate, BuildingRead
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.building_service import BuildingService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[BuildingRead],
    summary="List all buildings",
)
async def list_buildings(
    offset: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(50, ge=1, le=500, description="Max items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await BuildingService.list_all(db, offset=offset, limit=limit)
    return PaginatedResponse(
        items=[BuildingRead.model_validate(b, from_attributes=True) for b in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )


# =============================================================================
# CREATE A BUILDING
# =============================================================================
@router.post(
    "/",
    response_model=BuildingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new building",
)
async def create_building(
    payload: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)
    ),
):
    """
    Create a new building. Requires admin or facility_manager role.

    The building will be assigned a UUID automatically.
    """
    return await BuildingService.create(db, payload)


# =============================================================================
# GET A SINGLE BUILDING
# =============================================================================
@router.get(
    "/{building_id}",
    response_model=BuildingRead,
    summary="Get a building by ID",
)
async def get_building(
    building_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific building by its UUID.
    Returns 404 if the building does not exist.
    """
    building = await BuildingService.get_by_id(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    return building


# =============================================================================
# UPDATE A BUILDING (PARTIAL)
# =============================================================================
@router.patch(
    "/{building_id}",
    response_model=BuildingRead,
    summary="Update a building",
)
async def update_building(
    building_id: UUID,
    payload: BuildingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)
    ),
):
    """
    Partially update a building. Only provided fields are changed.
    Requires admin or facility_manager role.
    """
    building = await BuildingService.update(db, building_id, payload)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    return building


# =============================================================================
# DELETE A BUILDING
# =============================================================================
@router.delete(
    "/{building_id}",
    response_model=MessageResponse,
    summary="Delete a building",
)
async def delete_building(
    building_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)
    ),
):
    """
    Delete a building and all its zones (cascade delete).
    Requires admin or facility_manager role.
    This action is irreversible.
    """
    deleted = await BuildingService.delete(db, building_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    return MessageResponse(message="Building deleted successfully")
