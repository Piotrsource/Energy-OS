from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.alert_rule import AlertRuleCreate, AlertRuleUpdate, AlertRuleRead
from app.schemas.common import PaginatedResponse
from app.services.alert_rule_service import AlertRuleService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[AlertRuleRead],
    summary="List alert rules for a building",
)
async def list_rules(
    building_id: UUID = Query(...),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await AlertRuleService.list_by_building(db, building_id, offset=offset, limit=limit)
    return PaginatedResponse(
        items=[AlertRuleRead.model_validate(r) for r in items],
        total_count=total, offset=offset, limit=limit,
    )


@router.post("/", response_model=AlertRuleRead, status_code=status.HTTP_201_CREATED, summary="Create alert rule")
async def create_rule(
    data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = await AlertRuleService.create(db, data)
    await db.commit()
    return AlertRuleRead.model_validate(rule)


@router.patch("/{rule_id}", response_model=AlertRuleRead, summary="Update alert rule")
async def update_rule(
    rule_id: UUID,
    data: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = await AlertRuleService.update(db, rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    await db.commit()
    return AlertRuleRead.model_validate(rule)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete alert rule")
async def delete_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await AlertRuleService.delete(db, rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    await db.commit()
