# =============================================================================
# services/energy_meter_service.py — Energy Meter Business Logic
# =============================================================================
# PURPOSE: Handle energy meter data ingestion (bulk insert) and time-range
# queries. Provides the raw data layer that feeds the analytics service.
#
# METHODS:
#   bulk_insert()      → Insert multiple energy meter readings at once
#   query_readings()   → Retrieve meter data with time-range and filters
#
# NOTE: For aggregated analytics (energy summary, carbon emissions), see
# analytics_service.py which uses TimescaleDB's time_bucket() directly.
# =============================================================================

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.energy_meter import EnergyMeter
from app.schemas.energy_meter import EnergyMeterCreate


class EnergyMeterService:
    """Static methods for energy meter data ingestion and retrieval."""

    @staticmethod
    async def bulk_insert(
        db: AsyncSession, readings: list[EnergyMeterCreate]
    ) -> int:
        objects = [EnergyMeter(**r.model_dump()) for r in readings]
        db.add_all(objects)
        await db.flush()
        return len(objects)

    @staticmethod
    async def query_readings(
        db: AsyncSession,
        building_id: UUID,
        meter_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 0,
        limit: int = 500,
    ) -> tuple[list[EnergyMeter], int]:
        base = select(EnergyMeter).where(EnergyMeter.building_id == building_id)

        if meter_id:
            base = base.where(EnergyMeter.meter_id == meter_id)
        if start:
            base = base.where(EnergyMeter.time >= start)
        if end:
            base = base.where(EnergyMeter.time <= end)

        count_result = await db.execute(
            select(sa_func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            base.order_by(EnergyMeter.time.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total
