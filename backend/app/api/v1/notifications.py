from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationRead,
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.notification_service import NotificationService
from app.services.notification_preference_service import NotificationPreferenceService

router = APIRouter()


# ── Notifications ─────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=PaginatedResponse[NotificationRead],
    summary="List notifications for current user",
)
async def list_notifications(
    unread_only: bool = Query(False),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await NotificationService.list_for_user(
        db, current_user.id, unread_only=unread_only, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=[NotificationRead.model_validate(n) for n in items],
        total_count=total, offset=offset, limit=limit,
    )


@router.get("/unread-count", summary="Get unread notification count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await NotificationService.unread_count(db, current_user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=NotificationRead, summary="Mark notification as read")
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = await NotificationService.mark_read(db, notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.commit()
    return NotificationRead.model_validate(notif)


# ── Notification Preferences ──────────────────────────────────────────────


@router.get(
    "/preferences",
    response_model=NotificationPreferenceRead,
    summary="Get notification preferences for current user",
)
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = await NotificationPreferenceService.get_or_create(db, current_user.id)
    await db.commit()
    return NotificationPreferenceRead.model_validate(pref)


@router.patch(
    "/preferences",
    response_model=NotificationPreferenceRead,
    summary="Update notification preferences",
)
async def update_preferences(
    body: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updates = body.model_dump(exclude_unset=True)
    pref = await NotificationPreferenceService.update(db, current_user.id, updates)
    await db.commit()
    return NotificationPreferenceRead.model_validate(pref)
