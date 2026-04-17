from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.request import EnergyRequestCreate, EnergyRequestRead
from app.schemas.common import MessageResponse
from app.services.p2p.prosumer_service import ProsumerService
from app.services.p2p.marketplace_service import MarketplaceService

router = APIRouter()


@router.get(
    "/",
    response_model=list[EnergyRequestRead],
    summary="Browse buy requests",
)
async def list_requests(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await MarketplaceService.list_active_requests(db, limit, offset)


@router.post(
    "/",
    response_model=EnergyRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a buy request",
)
async def create_request(
    payload: EnergyRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    if payload.preferred_from >= payload.preferred_until:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "preferred_from must be before preferred_until")
    return await MarketplaceService.create_request(db, profile.id, payload)


@router.delete(
    "/{request_id}",
    response_model=MessageResponse,
    summary="Cancel a buy request",
)
async def cancel_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    deleted = await MarketplaceService.cancel_request(db, request_id, profile.id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Request not found or not yours")
    return MessageResponse(message="Request cancelled")
