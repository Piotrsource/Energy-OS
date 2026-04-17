from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.community import (
    CommunityCreate, CommunityRead, CommunityMemberRead, CommunityDashboard,
)
from app.schemas.common import MessageResponse
from app.services.p2p.prosumer_service import ProsumerService
from app.services.p2p.community_service import CommunityService

router = APIRouter()


@router.get(
    "/",
    response_model=list[CommunityRead],
    summary="List energy communities",
)
async def list_communities(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    communities = await CommunityService.list_all(db, limit, offset)
    result = []
    for c in communities:
        count = await CommunityService.get_member_count(db, c.id)
        read = CommunityRead(
            id=c.id,
            name=c.name,
            description=c.description,
            location_lat=c.location_lat,
            location_lng=c.location_lng,
            radius_km=c.radius_km,
            fee_discount_pct=c.fee_discount_pct,
            created_by=c.created_by,
            created_at=c.created_at,
            member_count=count,
        )
        result.append(read)
    return result


@router.post(
    "/",
    response_model=CommunityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an energy community",
)
async def create_community(
    payload: CommunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    community = await CommunityService.create(db, profile.id, payload)
    return CommunityRead(
        id=community.id,
        name=community.name,
        description=community.description,
        location_lat=community.location_lat,
        location_lng=community.location_lng,
        radius_km=community.radius_km,
        fee_discount_pct=community.fee_discount_pct,
        created_by=community.created_by,
        created_at=community.created_at,
        member_count=1,
    )


@router.post(
    "/{community_id}/join",
    response_model=MessageResponse,
    summary="Join a community",
)
async def join_community(
    community_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    community = await CommunityService.get_by_id(db, community_id)
    if not community:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Community not found")
    await CommunityService.join(db, community_id, profile.id)
    return MessageResponse(message="Joined community successfully")


@router.get(
    "/{community_id}/dashboard",
    response_model=CommunityDashboard,
    summary="Community trading dashboard",
)
async def community_dashboard(
    community_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await CommunityService.get_dashboard(db, community_id)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Community not found")
