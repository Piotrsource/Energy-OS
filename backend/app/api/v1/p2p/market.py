from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.market import MarketPrice, MarketStats
from app.services.p2p.pricing_engine import PricingEngine

router = APIRouter()


@router.get(
    "/price",
    response_model=MarketPrice,
    summary="Current suggested buy/sell prices",
)
async def get_market_price(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PricingEngine.get_market_price(db)


@router.get(
    "/stats",
    response_model=MarketStats,
    summary="Market statistics",
)
async def get_market_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PricingEngine.get_market_stats(db)
