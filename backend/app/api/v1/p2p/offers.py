from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.offer import OfferCreate, OfferRead
from app.schemas.common import MessageResponse
from app.services.p2p.prosumer_service import ProsumerService
from app.services.p2p.marketplace_service import MarketplaceService

router = APIRouter()


@router.get(
    "/",
    response_model=list[OfferRead],
    summary="Browse marketplace offers",
)
async def list_offers(
    max_price: int | None = Query(None, ge=1),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    return await MarketplaceService.list_active_offers(
        db, now=now, max_price=max_price, limit=limit, offset=offset,
    )


@router.post(
    "/",
    response_model=OfferRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a sell offer",
)
async def create_offer(
    payload: OfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    if payload.available_from >= payload.available_until:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "available_from must be before available_until")
    return await MarketplaceService.create_offer(db, profile.id, payload)


@router.delete(
    "/{offer_id}",
    response_model=MessageResponse,
    summary="Cancel an offer",
)
async def cancel_offer(
    offer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from uuid import UUID
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    deleted = await MarketplaceService.cancel_offer(db, UUID(offer_id), profile.id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Offer not found or not yours")
    return MessageResponse(message="Offer cancelled")
