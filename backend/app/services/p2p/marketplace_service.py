from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.energy_offer import EnergyOffer, OfferStatus
from app.models.p2p.energy_request import EnergyRequest, RequestStatus
from app.models.p2p.prosumer_profile import ProsumerProfile
from app.schemas.p2p.offer import OfferCreate
from app.schemas.p2p.request import EnergyRequestCreate


class MarketplaceService:

    # ---- OFFERS (sell side) ----

    @staticmethod
    async def create_offer(
        db: AsyncSession, seller_id: UUID, data: OfferCreate,
    ) -> EnergyOffer:
        offer = EnergyOffer(
            seller_id=seller_id,
            quantity_wh=data.quantity_wh,
            price_cents_per_kwh=data.price_cents_per_kwh,
            available_from=data.available_from,
            available_until=data.available_until,
            min_purchase_wh=data.min_purchase_wh,
            remaining_wh=data.quantity_wh,
            auto_renew=data.auto_renew,
        )
        db.add(offer)
        await db.flush()
        return offer

    @staticmethod
    async def list_active_offers(
        db: AsyncSession,
        now: datetime | None = None,
        max_price: int | None = None,
        seller_lat: float | None = None,
        seller_lng: float | None = None,
        radius_km: float = 50.0,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EnergyOffer]:
        q = select(EnergyOffer).where(
            EnergyOffer.status.in_([OfferStatus.ACTIVE, OfferStatus.PARTIALLY_FILLED]),
            EnergyOffer.remaining_wh > 0,
        )
        if now:
            q = q.where(
                EnergyOffer.available_from <= now,
                EnergyOffer.available_until >= now,
            )
        if max_price is not None:
            q = q.where(EnergyOffer.price_cents_per_kwh <= max_price)

        # Proximity filter: simplified Euclidean approximation
        # (PostGIS would be used in production for accurate geo queries)
        if seller_lat is not None and seller_lng is not None:
            km_per_deg = 111.0
            lat_range = radius_km / km_per_deg
            lng_range = radius_km / (km_per_deg * func.cos(func.radians(seller_lat)))
            q = q.join(ProsumerProfile, ProsumerProfile.id == EnergyOffer.seller_id)
            q = q.where(
                ProsumerProfile.lat.between(seller_lat - lat_range, seller_lat + lat_range),
                ProsumerProfile.lng.between(seller_lng - lng_range, seller_lng + lng_range),
            )

        q = q.order_by(EnergyOffer.price_cents_per_kwh.asc()).limit(limit).offset(offset)
        result = await db.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_offer(db: AsyncSession, offer_id: UUID) -> EnergyOffer | None:
        result = await db.execute(
            select(EnergyOffer).where(EnergyOffer.id == offer_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def cancel_offer(db: AsyncSession, offer_id: UUID, seller_id: UUID) -> bool:
        offer = await MarketplaceService.get_offer(db, offer_id)
        if not offer or offer.seller_id != seller_id:
            return False
        offer.status = OfferStatus.CANCELLED
        await db.flush()
        return True

    @staticmethod
    async def get_offers_by_seller(
        db: AsyncSession, seller_id: UUID, limit: int = 50,
    ) -> list[EnergyOffer]:
        result = await db.execute(
            select(EnergyOffer)
            .where(EnergyOffer.seller_id == seller_id)
            .order_by(EnergyOffer.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ---- REQUESTS (buy side) ----

    @staticmethod
    async def create_request(
        db: AsyncSession, buyer_id: UUID, data: EnergyRequestCreate,
    ) -> EnergyRequest:
        req = EnergyRequest(
            buyer_id=buyer_id,
            quantity_wh=data.quantity_wh,
            max_price_cents_per_kwh=data.max_price_cents_per_kwh,
            preferred_from=data.preferred_from,
            preferred_until=data.preferred_until,
            remaining_wh=data.quantity_wh,
        )
        db.add(req)
        await db.flush()
        return req

    @staticmethod
    async def list_active_requests(
        db: AsyncSession, limit: int = 50, offset: int = 0,
    ) -> list[EnergyRequest]:
        result = await db.execute(
            select(EnergyRequest)
            .where(
                EnergyRequest.status.in_([RequestStatus.ACTIVE, RequestStatus.PARTIALLY_FILLED]),
                EnergyRequest.remaining_wh > 0,
            )
            .order_by(EnergyRequest.max_price_cents_per_kwh.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def cancel_request(db: AsyncSession, request_id: UUID, buyer_id: UUID) -> bool:
        result = await db.execute(
            select(EnergyRequest).where(EnergyRequest.id == request_id)
        )
        req = result.scalar_one_or_none()
        if not req or req.buyer_id != buyer_id:
            return False
        req.status = RequestStatus.CANCELLED
        await db.flush()
        return True

    @staticmethod
    async def get_requests_by_buyer(
        db: AsyncSession, buyer_id: UUID, limit: int = 50,
    ) -> list[EnergyRequest]:
        result = await db.execute(
            select(EnergyRequest)
            .where(EnergyRequest.buyer_id == buyer_id)
            .order_by(EnergyRequest.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
