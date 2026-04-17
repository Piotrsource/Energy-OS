"""
Dynamic Pricing Engine — suggests optimal buy/sell prices.

Factors:
  - Grid retail rate (configurable baseline)
  - Time-of-use period (peak / off-peak / shoulder)
  - Local supply/demand ratio from active offers and requests
  - Historical clearing prices from recent orders

Price guidance:
  - Sellers should undercut grid retail to attract buyers
  - Buyers should offer above wholesale to attract sellers
  - Platform suggests a midpoint that benefits both parties
"""
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.energy_offer import EnergyOffer, OfferStatus
from app.models.p2p.energy_request import EnergyRequest, RequestStatus
from app.models.p2p.p2p_order import P2POrder, OrderStatus
from app.schemas.p2p.market import MarketPrice, MarketStats

GRID_RETAIL_CENTS = 25
GRID_WHOLESALE_CENTS = 5


class PricingEngine:

    @staticmethod
    def _get_tou_period(hour: int) -> str:
        if 16 <= hour < 21:
            return "peak"
        elif 7 <= hour < 16 or 21 <= hour < 23:
            return "shoulder"
        else:
            return "off_peak"

    @staticmethod
    def _tou_multiplier(period: str) -> float:
        return {"peak": 1.3, "shoulder": 1.0, "off_peak": 0.7}.get(period, 1.0)

    @staticmethod
    async def get_market_price(db: AsyncSession) -> MarketPrice:
        now = datetime.now(timezone.utc)
        period = PricingEngine._get_tou_period(now.hour)
        multiplier = PricingEngine._tou_multiplier(period)

        # Supply / demand ratio
        supply = await db.execute(
            select(func.coalesce(func.sum(EnergyOffer.remaining_wh), 0))
            .where(EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]))
        )
        total_supply = supply.scalar() or 0

        demand = await db.execute(
            select(func.coalesce(func.sum(EnergyRequest.remaining_wh), 0))
            .where(EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]))
        )
        total_demand = demand.scalar() or 0

        ratio = (total_supply / total_demand) if total_demand > 0 else 2.0

        # When supply > demand, prices go down; when demand > supply, prices go up
        supply_adjustment = max(0.7, min(1.3, 1.0 / ratio)) if ratio > 0 else 1.0

        base_sell = int(GRID_RETAIL_CENTS * 0.6 * multiplier * supply_adjustment)
        base_buy = int(GRID_RETAIL_CENTS * 0.75 * multiplier * supply_adjustment)

        base_sell = max(GRID_WHOLESALE_CENTS + 1, base_sell)
        base_buy = min(GRID_RETAIL_CENTS - 1, max(base_sell + 1, base_buy))

        return MarketPrice(
            suggested_sell_cents_per_kwh=base_sell,
            suggested_buy_cents_per_kwh=base_buy,
            grid_retail_cents_per_kwh=GRID_RETAIL_CENTS,
            grid_wholesale_cents_per_kwh=GRID_WHOLESALE_CENTS,
            supply_demand_ratio=round(ratio, 2),
            time_of_use_period=period,
        )

    @staticmethod
    async def get_market_stats(db: AsyncSession) -> MarketStats:
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(hours=24)

        active_offer_count = (await db.execute(
            select(func.count()).select_from(EnergyOffer)
            .where(EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]))
        )).scalar() or 0

        active_request_count = (await db.execute(
            select(func.count()).select_from(EnergyRequest)
            .where(EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]))
        )).scalar() or 0

        total_available = (await db.execute(
            select(func.coalesce(func.sum(EnergyOffer.remaining_wh), 0))
            .where(EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]))
        )).scalar() or 0

        total_requested = (await db.execute(
            select(func.coalesce(func.sum(EnergyRequest.remaining_wh), 0))
            .where(EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]))
        )).scalar() or 0

        avg_offer = (await db.execute(
            select(func.coalesce(func.avg(EnergyOffer.price_cents_per_kwh), 0))
            .where(EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]))
        )).scalar() or 0.0

        avg_request = (await db.execute(
            select(func.coalesce(func.avg(EnergyRequest.max_price_cents_per_kwh), 0))
            .where(EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]))
        )).scalar() or 0.0

        trades_24h = (await db.execute(
            select(func.count()).select_from(P2POrder)
            .where(P2POrder.matched_at >= day_ago)
        )).scalar() or 0

        volume_24h = (await db.execute(
            select(func.coalesce(func.sum(P2POrder.matched_wh), 0))
            .where(P2POrder.matched_at >= day_ago)
        )).scalar() or 0

        return MarketStats(
            active_offers=active_offer_count,
            active_requests=active_request_count,
            total_available_wh=total_available,
            total_requested_wh=total_requested,
            avg_offer_price_cents=round(float(avg_offer), 1),
            avg_request_price_cents=round(float(avg_request), 1),
            trades_last_24h=trades_24h,
            volume_last_24h_wh=volume_24h,
        )
