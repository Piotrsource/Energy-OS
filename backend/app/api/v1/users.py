# =============================================================================
# api/v1/users.py — User Management Router
# =============================================================================
# PURPOSE: Handle HTTP requests for user CRUD operations.
# User management is restricted to administrators.
#
# ENDPOINTS:
#   GET   /api/v1/users         → List all users (admin only)
#   POST  /api/v1/users         → Create a new user (admin only)
#   PATCH /api/v1/users/{id}    → Update a user (admin only)
#
# ACCESS CONTROL:
#   All endpoints require admin role. Facility managers and technicians
#   cannot manage other users.
#
# SECURITY:
#   - Passwords are hashed before storage (handled by UserService)
#   - The password_hash field is NEVER returned in responses (UserRead schema)
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[UserRead],
    summary="List all users",
)
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    items, total = await UserService.list_all(db, offset=offset, limit=limit)
    return PaginatedResponse(
        items=[UserRead.model_validate(u, from_attributes=True) for u in items],
        total_count=total,
        offset=offset,
        limit=limit,
    )


# =============================================================================
# CREATE A USER
# =============================================================================
@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """
    Create a new platform user. Admin only.

    The password will be hashed with bcrypt before storage.
    Valid roles: admin, facility_manager, technician.
    """
    # Check for duplicate email
    existing = await UserService.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    return await UserService.create(db, payload)


# =============================================================================
# UPDATE A USER
# =============================================================================
@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """
    Partially update a user's profile. Admin only.
    Only provided fields are changed. If a new password is provided,
    it will be hashed before storage.
    """
    user = await UserService.update(db, user_id, payload)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
