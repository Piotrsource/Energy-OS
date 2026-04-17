from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.p2p_order import P2POrder, OrderStatus
from app.models.p2p.p2p_settlement import P2PSettlement
from app.models.p2p.energy_offer import EnergyOffer, OfferStatus
from app.models.p2p.energy_request import EnergyRequest, RequestStatus
from app.models.p2p.p2p_tax_summary import P2PTaxSummary
from app.schemas.p2p.analytics import SellerAnalytics, BuyerAnalytics, TaxSummaryRead

CO2_PER_KWH = 0.4  # kg CO2 per kWh offset by local clean energy
GRID_RETAIL_CENTS = 25  # baseline for savings calculation


class P2PAnalyticsService:

    @staticmethod
    async def seller_analytics(db: AsyncSession, prosumer_id: UUID) -> SellerAnalytics:
        settlements = await db.execute(
            select(
                func.coalesce(func.sum(P2PSettlement.actual_delivered_wh), 0),
                func.coalesce(func.sum(P2PSettlement.seller_credit_cents), 0),
                func.count(),
            )
            .join(P2POrder, P2POrder.id == P2PSettlement.order_id)
            .where(P2POrder.seller_id == prosumer_id)
        )
        row = settlements.one()
        total_wh = row[0] or 0
        total_revenue = row[1] or 0
        completed = row[2] or 0

        kwh_sold = total_wh / 1000
        avg_price = (total_revenue * 1000 / total_wh) if total_wh > 0 else 0.0

        active_offers = (await db.execute(
            select(func.count()).select_from(EnergyOffer)
            .where(
                EnergyOffer.seller_id == prosumer_id,
                EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]),
            )
        )).scalar() or 0

        # Rough monthly projection based on last 30 days of revenue
        monthly_projection = int(total_revenue * 30 / max(1, completed))

        return SellerAnalytics(
            total_kwh_sold=round(kwh_sold, 2),
            total_revenue_cents=total_revenue,
            avg_sell_price_cents_per_kwh=round(avg_price, 1),
            production_vs_sold_ratio=0.0,
            active_offers=active_offers,
            completed_orders=completed,
            earnings_projection_monthly_cents=monthly_projection,
        )

    @staticmethod
    async def buyer_analytics(db: AsyncSession, prosumer_id: UUID) -> BuyerAnalytics:
        settlements = await db.execute(
            select(
                func.coalesce(func.sum(P2PSettlement.actual_delivered_wh), 0),
                func.coalesce(func.sum(P2PSettlement.buyer_debit_cents), 0),
                func.count(),
            )
            .join(P2POrder, P2POrder.id == P2PSettlement.order_id)
            .where(P2POrder.buyer_id == prosumer_id)
        )
        row = settlements.one()
        total_wh = row[0] or 0
        total_spent = row[1] or 0
        completed = row[2] or 0

        kwh_bought = total_wh / 1000
        avg_price = (total_spent * 1000 / total_wh) if total_wh > 0 else 0.0

        # Savings vs grid retail
        grid_cost = int(kwh_bought * GRID_RETAIL_CENTS)
        savings = grid_cost - total_spent

        active_requests = (await db.execute(
            select(func.count()).select_from(EnergyRequest)
            .where(
                EnergyRequest.buyer_id == prosumer_id,
                EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]),
            )
        )).scalar() or 0

        carbon = kwh_bought * CO2_PER_KWH

        return BuyerAnalytics(
            total_kwh_bought=round(kwh_bought, 2),
            total_spent_cents=total_spent,
            avg_buy_price_cents_per_kwh=round(avg_price, 1),
            savings_vs_grid_cents=savings,
            carbon_offset_kg=round(carbon, 2),
            active_requests=active_requests,
            completed_orders=completed,
        )

    @staticmethod
    async def get_tax_summary(db: AsyncSession, prosumer_id: UUID, year: int) -> TaxSummaryRead:
        result = await db.execute(
            select(P2PTaxSummary).where(
                P2PTaxSummary.user_id == prosumer_id,
                P2PTaxSummary.tax_year == year,
            )
        )
        summary = result.scalar_one_or_none()

        if summary:
            return TaxSummaryRead(
                tax_year=summary.tax_year,
                total_earnings_cents=summary.total_earnings_cents,
                total_kwh_sold=summary.total_kwh_sold,
                requires_1099=summary.total_earnings_cents >= 60000,
            )

        # Compute on-the-fly from settlements
        year_start = datetime(year, 1, 1, tzinfo=timezone.utc)
        year_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

        row = (await db.execute(
            select(
                func.coalesce(func.sum(P2PSettlement.seller_credit_cents), 0),
                func.coalesce(func.sum(P2PSettlement.actual_delivered_wh), 0),
            )
            .join(P2POrder, P2POrder.id == P2PSettlement.order_id)
            .where(
                P2POrder.seller_id == prosumer_id,
                P2PSettlement.created_at >= year_start,
                P2PSettlement.created_at < year_end,
            )
        )).one()

        earnings = row[0] or 0
        kwh = (row[1] or 0) // 1000

        return TaxSummaryRead(
            tax_year=year,
            total_earnings_cents=earnings,
            total_kwh_sold=kwh,
            requires_1099=earnings >= 60000,
        )
