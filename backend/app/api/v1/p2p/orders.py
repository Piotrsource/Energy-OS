from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.p2p.p2p_order import P2POrder
from app.models.p2p.p2p_settlement import P2PSettlement
from app.schemas.p2p.order import OrderRead
from app.schemas.p2p.settlement import SettlementRead
from app.services.p2p.prosumer_service import ProsumerService

router = APIRouter()


@router.get(
    "/",
    response_model=list[OrderRead],
    summary="List my orders (as seller or buyer)",
)
async def list_orders(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")

    result = await db.execute(
        select(P2POrder)
        .where(or_(P2POrder.seller_id == profile.id, P2POrder.buyer_id == profile.id))
        .order_by(P2POrder.matched_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Order detail",
)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")

    result = await db.execute(select(P2POrder).where(P2POrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order or (order.seller_id != profile.id and order.buyer_id != profile.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return order


@router.get(
    "/{order_id}/settlements",
    response_model=list[SettlementRead],
    summary="Settlement records for an order",
)
async def get_settlements(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(P2PSettlement)
        .where(P2PSettlement.order_id == order_id)
        .order_by(P2PSettlement.interval_start.desc())
    )
    return list(result.scalars().all())
