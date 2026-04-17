"""
Settlement Engine — reconciles actual meter data with matched orders.

For each 15-minute interval:
  1. Read actual meter data for seller (net export) and buyer (consumption)
  2. Settle at contracted price for actual delivered kWh (not contracted)
  3. Handle shortfall: if seller exported less than contracted → partial settlement
  4. Calculate platform fee (configurable, default 2%)
  5. Update wallet balances via double-entry ledger
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.p2p_order import P2POrder, OrderStatus
from app.models.p2p.p2p_settlement import P2PSettlement
from app.models.p2p.meter_reading_p2p import MeterReadingP2P
from app.models.p2p.energy_wallet import EnergyWallet
from app.services.p2p.wallet_service import WalletService

PLATFORM_FEE_PCT = 2  # 2% default


class SettlementEngine:

    @staticmethod
    async def settle_interval(
        db: AsyncSession,
        interval_start: datetime,
        interval_end: datetime,
    ) -> list[P2PSettlement]:
        """Settle all matched orders for a given 15-minute interval."""
        orders_result = await db.execute(
            select(P2POrder).where(
                P2POrder.status.in_([OrderStatus.MATCHED, OrderStatus.SETTLING]),
            )
        )
        orders = list(orders_result.scalars().all())
        settlements: list[P2PSettlement] = []

        for order in orders:
            # Check idempotency — skip if already settled for this interval
            existing = await db.execute(
                select(P2PSettlement).where(
                    P2PSettlement.order_id == order.id,
                    P2PSettlement.interval_start == interval_start,
                )
            )
            if existing.scalar_one_or_none():
                continue

            seller_meter = await SettlementEngine._get_meter_reading(
                db, order.seller_id, interval_start, interval_end,
            )
            buyer_meter = await SettlementEngine._get_meter_reading(
                db, order.buyer_id, interval_start, interval_end,
            )

            seller_export = seller_meter.net_export_wh if seller_meter else 0
            contracted_wh = order.matched_wh

            # Actual delivered is the lesser of contracted and actually exported
            actual_wh = min(contracted_wh, max(0, seller_export))
            shortfall = actual_wh < contracted_wh

            # Calculate settlement amounts (price is per kWh, energy in Wh)
            settlement_cents = (actual_wh * order.price_cents_per_kwh) // 1000
            fee_cents = (settlement_cents * PLATFORM_FEE_PCT) // 100
            seller_credit = settlement_cents - fee_cents
            buyer_debit = settlement_cents

            settlement = P2PSettlement(
                order_id=order.id,
                interval_start=interval_start,
                interval_end=interval_end,
                contracted_wh=contracted_wh,
                actual_delivered_wh=actual_wh,
                settlement_cents=settlement_cents,
                platform_fee_cents=fee_cents,
                seller_credit_cents=seller_credit,
                buyer_debit_cents=buyer_debit,
                shortfall_flag=shortfall,
            )
            db.add(settlement)
            settlements.append(settlement)

            # Update wallets
            seller_wallet = await WalletService.get_by_prosumer_id(db, order.seller_id)
            buyer_wallet = await WalletService.get_by_prosumer_id(db, order.buyer_id)
            if seller_wallet and buyer_wallet and settlement_cents > 0:
                await WalletService.credit_sale(
                    db, seller_wallet, buyer_wallet,
                    amount_cents=buyer_debit,
                    energy_wh=actual_wh,
                    platform_fee_cents=fee_cents,
                    order_id=order.id,
                )

            order.status = OrderStatus.SETTLING

        await db.flush()
        return settlements

    @staticmethod
    async def finalize_orders(db: AsyncSession) -> int:
        """Mark orders whose time window has passed as settled."""
        now = datetime.now(timezone.utc)
        count = 0

        result = await db.execute(
            select(P2POrder).where(P2POrder.status == OrderStatus.SETTLING)
        )
        for order in result.scalars().all():
            # Load the related offer to check time window
            from app.models.p2p.energy_offer import EnergyOffer
            offer_result = await db.execute(
                select(EnergyOffer).where(EnergyOffer.id == order.offer_id)
            )
            offer = offer_result.scalar_one_or_none()
            if offer and offer.available_until < now:
                order.status = OrderStatus.SETTLED
                order.settled_at = now
                count += 1

        await db.flush()
        return count

    @staticmethod
    async def _get_meter_reading(
        db: AsyncSession,
        prosumer_id: UUID,
        interval_start: datetime,
        interval_end: datetime,
    ) -> MeterReadingP2P | None:
        result = await db.execute(
            select(MeterReadingP2P).where(
                MeterReadingP2P.user_id == prosumer_id,
                MeterReadingP2P.time >= interval_start,
                MeterReadingP2P.time < interval_end,
            )
            .order_by(MeterReadingP2P.time.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
