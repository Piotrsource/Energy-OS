from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.alert import AlertRead, AlertAcknowledge
from app.schemas.common import PaginatedResponse
from app.services.alert_service import AlertService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[AlertRead],
    summary="List alerts for a building",
)
async def list_alerts(
    building_id: UUID = Query(...),
    acknowledged: bool | None = Query(None, description="Filter by acknowledgment status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await AlertService.list_by_building(
        db, building_id, acknowledged=acknowledged, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=[AlertRead.model_validate(a) for a in items],
        total_count=total, offset=offset, limit=limit,
    )


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AlertRead,
    summary="Acknowledge an alert",
)
async def acknowledge_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await AlertService.acknowledge(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.commit()
    return AlertRead.model_validate(alert)
