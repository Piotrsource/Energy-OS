from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.analytics import SellerAnalytics, BuyerAnalytics, TaxSummaryRead
from app.services.p2p.prosumer_service import ProsumerService
from app.services.p2p.analytics_service import P2PAnalyticsService

router = APIRouter()


@router.get(
    "/seller",
    response_model=SellerAnalytics,
    summary="Seller analytics — revenue, kWh sold, projections",
)
async def seller_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return await P2PAnalyticsService.seller_analytics(db, profile.id)


@router.get(
    "/buyer",
    response_model=BuyerAnalytics,
    summary="Buyer analytics — savings, kWh bought, carbon offset",
)
async def buyer_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return await P2PAnalyticsService.buyer_analytics(db, profile.id)


@router.get(
    "/tax-summary",
    response_model=TaxSummaryRead,
    summary="Annual tax summary for reporting",
)
async def tax_summary(
    year: int = Query(..., ge=2020, le=2030),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return await P2PAnalyticsService.get_tax_summary(db, profile.id, year)
