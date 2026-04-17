# =============================================================================
# api/v1/forecasts.py — Forecast Router
# =============================================================================
# PURPOSE: Handle AI forecast storage and retrieval.
# Forecasts are created by the ML pipeline and displayed on the dashboard.
#
# ENDPOINTS:
#   POST /api/v1/forecasts              → Insert a new forecast
#   GET  /api/v1/forecasts?building_id= → Get forecasts for a building
#
# ACCESS CONTROL:
#   - POST: Admin or Facility Manager (AI pipeline uses a service account)
#   - GET:  Any authenticated user
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.forecast import ForecastCreate, ForecastRead
from app.schemas.common import PaginatedResponse
from app.services.forecast_service import ForecastService

router = APIRouter()


@router.post(
    "/",
    response_model=ForecastRead,
    status_code=status.HTTP_201_CREATED,
    summary="Insert an AI forecast",
)
async def create_forecast(
    payload: ForecastCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)
    ),
):
    return await ForecastService.create(db, payload)


@router.get(
    "/",
    response_model=PaginatedResponse[ForecastRead],
    summary="Get forecasts for a building",
)
async def list_forecasts(
    building_id: UUID = Query(..., description="Building to get forecasts for"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await ForecastService.list_by_building(
        db, building_id, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=[ForecastRead.model_validate(f, from_attributes=True) for f in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )
