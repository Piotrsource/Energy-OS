# =============================================================================
# api/v1/recommendations.py — Recommendation Router
# =============================================================================
# PURPOSE: Handle AI recommendation CRUD and lifecycle management.
#
# Recommendations follow a lifecycle:
#   pending → approved → applied   (happy path)
#   pending → rejected             (user overrides AI)
#   approved → rejected            (user changes mind)
#
# ENDPOINTS:
#   POST  /api/v1/recommendations       → Insert a new recommendation
#   GET   /api/v1/recommendations?building_id= → List recommendations
#   PATCH /api/v1/recommendations/{id}  → Update status (approve/apply/reject)
#
# ACCESS CONTROL:
#   - POST:  Admin or Facility Manager (optimization engine)
#   - GET:   Any authenticated user
#   - PATCH: Any authenticated user (technicians can approve/reject in the field)
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationRead,
)
from app.schemas.common import PaginatedResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post(
    "/",
    response_model=RecommendationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Insert an AI recommendation",
)
async def create_recommendation(
    payload: RecommendationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)
    ),
):
    return await RecommendationService.create(db, payload)


@router.get(
    "/",
    response_model=PaginatedResponse[RecommendationRead],
    summary="List recommendations for a building",
)
async def list_recommendations(
    building_id: UUID = Query(..., description="Building to get recommendations for"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await RecommendationService.list_by_building(
        db, building_id, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=[RecommendationRead.model_validate(r, from_attributes=True) for r in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )


# =============================================================================
# UPDATE RECOMMENDATION STATUS
# =============================================================================
@router.patch(
    "/{recommendation_id}",
    response_model=RecommendationRead,
    summary="Update recommendation status",
)
async def update_recommendation(
    recommendation_id: UUID,
    payload: RecommendationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a recommendation's lifecycle status.

    Valid status values: approved, applied, rejected
    When status is set to "applied", the applied_at timestamp is
    automatically set to the current time (unless explicitly provided).

    Any authenticated user can update status (technicians need this
    to approve/reject recommendations in the field).
    """
    # Validate status value
    valid_statuses = {"pending", "approved", "applied", "rejected"}
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    recommendation = await RecommendationService.update_status(
        db, recommendation_id, payload
    )
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )
    return recommendation
