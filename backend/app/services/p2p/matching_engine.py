"""
Order Matching Engine — runs every 15 minutes (aligned with meter intervals).

Algorithm:
  1. Fetch all active offers sorted by price ASC (cheapest first)
  2. Fetch all active requests sorted by max_price DESC (highest bidder first)
  3. For each request, find compatible offers where:
     - buyer's max_price >= seller's ask price
     - time windows overlap
     - offer has remaining quantity >= min_purchase threshold
  4. Match at the seller's ask price (seller-favorable for liquidity)
  5. Support partial fills: a 10 kWh offer can match 3 separate requests
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.energy_offer import EnergyOffer, OfferStatus
from app.models.p2p.energy_request import EnergyRequest, RequestStatus
from app.models.p2p.p2p_order import P2POrder, OrderStatus


class MatchingEngine:

    @staticmethod
    async def run_matching_cycle(db: AsyncSession) -> list[P2POrder]:
        """Execute one matching cycle. Returns all newly created orders."""
        now = datetime.now(timezone.utc)

        offers_result = await db.execute(
            select(EnergyOffer)
            .where(
                EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]),
                EnergyOffer.remaining_wh > 0,
                EnergyOffer.available_from <= now,
                EnergyOffer.available_until >= now,
            )
            .order_by(EnergyOffer.price_cents_per_kwh.asc())
        )
        offers = list(offers_result.scalars().all())

        requests_result = await db.execute(
            select(EnergyRequest)
            .where(
                EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]),
                EnergyRequest.remaining_wh > 0,
                EnergyRequest.preferred_from <= now,
                EnergyRequest.preferred_until >= now,
            )
            .order_by(EnergyRequest.max_price_cents_per_kwh.desc())
        )
        requests = list(requests_result.scalars().all())

        new_orders: list[P2POrder] = []

        for req in requests:
            if req.remaining_wh <= 0:
                continue

            for offer in offers:
                if offer.remaining_wh <= 0:
                    continue

                # Skip self-trade
                if offer.seller_id == req.buyer_id:
                    continue

                # Price compatibility: buyer willing to pay at least the ask
                if req.max_price_cents_per_kwh < offer.price_cents_per_kwh:
                    continue

                # Minimum purchase check
                if offer.min_purchase_wh > 0 and req.remaining_wh < offer.min_purchase_wh:
                    continue

                matched_wh = min(offer.remaining_wh, req.remaining_wh)

                order = P2POrder(
                    offer_id=offer.id,
                    request_id=req.id,
                    seller_id=offer.seller_id,
                    buyer_id=req.buyer_id,
                    matched_wh=matched_wh,
                    price_cents_per_kwh=offer.price_cents_per_kwh,
                    status=OrderStatus.MATCHED,
                )
                db.add(order)
                new_orders.append(order)

                offer.remaining_wh -= matched_wh
                req.remaining_wh -= matched_wh

                if offer.remaining_wh <= 0:
                    offer.status = OfferStatus.FILLED
                else:
                    offer.status = OfferStatus.PARTIALLY_FILLED

                if req.remaining_wh <= 0:
                    req.status = RequestStatus.FILLED
                    break
                else:
                    req.status = RequestStatus.PARTIALLY_FILLED

        await db.flush()
        return new_orders

    @staticmethod
    async def expire_stale(db: AsyncSession) -> int:
        """Mark offers/requests past their window as expired."""
        now = datetime.now(timezone.utc)
        count = 0

        offers_result = await db.execute(
            select(EnergyOffer).where(
                EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]),
                EnergyOffer.available_until < now,
            )
        )
        for offer in offers_result.scalars().all():
            offer.status = OfferStatus.EXPIRED
            count += 1

        requests_result = await db.execute(
            select(EnergyRequest).where(
                EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]),
                EnergyRequest.preferred_until < now,
            )
        )
        for req in requests_result.scalars().all():
            req.status = RequestStatus.EXPIRED
            count += 1

        await db.flush()
        return count
