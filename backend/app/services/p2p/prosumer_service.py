from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.prosumer_profile import ProsumerProfile, ProsumerStatus
from app.models.p2p.energy_wallet import EnergyWallet
from app.models.p2p.meter_reading_p2p import MeterReadingP2P
from app.schemas.p2p.prosumer import ProsumerCreate, ProsumerUpdate, MeterReadingCreate


class ProsumerService:

    @staticmethod
    async def register(db: AsyncSession, user_id: UUID, data: ProsumerCreate) -> ProsumerProfile:
        profile = ProsumerProfile(
            user_id=user_id,
            address=data.address,
            lat=data.lat,
            lng=data.lng,
            solar_capacity_kw=data.solar_capacity_kw,
            battery_capacity_kwh=data.battery_capacity_kwh,
            inverter_type=data.inverter_type,
            meter_id=data.meter_id,
            meter_provider=data.meter_provider,
            status=ProsumerStatus.ACTIVE if data.accept_grid_agreement else ProsumerStatus.PENDING,
            grid_agreement_accepted_at=(
                datetime.now(timezone.utc) if data.accept_grid_agreement else None
            ),
        )
        db.add(profile)
        await db.flush()

        wallet = EnergyWallet(user_id=profile.id)
        db.add(wallet)
        await db.flush()

        return profile

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: UUID) -> ProsumerProfile | None:
        result = await db.execute(
            select(ProsumerProfile).where(ProsumerProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, profile_id: UUID) -> ProsumerProfile | None:
        result = await db.execute(
            select(ProsumerProfile).where(ProsumerProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, profile_id: UUID, data: ProsumerUpdate) -> ProsumerProfile | None:
        profile = await ProsumerService.get_by_id(db, profile_id)
        if not profile:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        await db.flush()
        return profile

    @staticmethod
    async def ingest_meter_readings(
        db: AsyncSession, user_id: UUID, readings: list[MeterReadingCreate],
    ) -> int:
        profile = await ProsumerService.get_by_user_id(db, user_id)
        if not profile:
            return 0
        objects = [
            MeterReadingP2P(
                time=r.time,
                meter_id=r.meter_id,
                user_id=profile.id,
                production_wh=r.production_wh,
                consumption_wh=r.consumption_wh,
                net_export_wh=r.net_export_wh,
                source=r.source,
            )
            for r in readings
        ]
        db.add_all(objects)
        await db.flush()
        return len(objects)

    @staticmethod
    async def get_meter_readings(
        db: AsyncSession,
        profile_id: UUID,
        start: datetime,
        end: datetime,
        limit: int = 200,
    ) -> list[MeterReadingP2P]:
        result = await db.execute(
            select(MeterReadingP2P)
            .where(
                MeterReadingP2P.user_id == profile_id,
                MeterReadingP2P.time >= start,
                MeterReadingP2P.time <= end,
            )
            .order_by(MeterReadingP2P.time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
