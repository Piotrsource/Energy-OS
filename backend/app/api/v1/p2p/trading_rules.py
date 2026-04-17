from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.trading_rule import (
    TradingRuleCreate, TradingRuleUpdate, TradingRuleRead, TradingRuleTestResult,
)
from app.schemas.common import MessageResponse
from app.services.p2p.prosumer_service import ProsumerService
from app.services.p2p.trading_rule_service import TradingRuleService

router = APIRouter()


@router.get(
    "/",
    response_model=list[TradingRuleRead],
    summary="List my trading rules",
)
async def list_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return await TradingRuleService.list_by_user(db, profile.id)


@router.post(
    "/",
    response_model=TradingRuleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a trading rule",
)
async def create_rule(
    payload: TradingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return await TradingRuleService.create(db, profile.id, payload)


@router.patch(
    "/{rule_id}",
    response_model=TradingRuleRead,
    summary="Update a trading rule",
)
async def update_rule(
    rule_id: UUID,
    payload: TradingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    rule = await TradingRuleService.update(db, rule_id, profile.id, payload)
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found or not yours")
    return rule


@router.delete(
    "/{rule_id}",
    response_model=MessageResponse,
    summary="Delete a trading rule",
)
async def delete_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    deleted = await TradingRuleService.delete(db, rule_id, profile.id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found or not yours")
    return MessageResponse(message="Trading rule deleted")


@router.post(
    "/{rule_id}/test",
    response_model=TradingRuleTestResult,
    summary="Dry-run a rule against current market",
)
async def test_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    rule = await TradingRuleService.get_by_id(db, rule_id)
    if not rule or rule.user_id != profile.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")

    return TradingRuleTestResult(
        rule_id=rule.id,
        would_trigger=rule.enabled,
        reason="Dry-run simulation — rule would create offer/request based on conditions",
        simulated_offer=rule.action_json if rule.rule_type.value == "auto_sell" else None,
        simulated_request=rule.action_json if rule.rule_type.value == "auto_buy" else None,
    )
