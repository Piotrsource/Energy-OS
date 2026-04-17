# =============================================================================
# services/hvac_service.py — HVAC Status Business Logic
# =============================================================================
# PURPOSE: Handle HVAC status data ingestion (bulk insert) and time-range
# queries. Similar to sensor_service.py but for HVAC equipment state tracking.
#
# METHODS:
#   bulk_insert()      → Insert multiple HVAC status snapshots at once
#   query_status()     → Retrieve status history with time-range and filters
# =============================================================================

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hvac_status import HvacStatus
from app.schemas.hvac import HvacStatusCreate


class HvacService:
    """Static methods for HVAC status ingestion and retrieval."""

    @staticmethod
    async def bulk_insert(
        db: AsyncSession, entries: list[HvacStatusCreate]
    ) -> int:
        objects = [HvacStatus(**e.model_dump()) for e in entries]
        db.add_all(objects)
        await db.flush()
        return len(objects)

    @staticmethod
    async def query_status(
        db: AsyncSession,
        building_id: UUID,
        zone_id: UUID | None = None,
        device_type: str | None = None,
        status_filter: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 0,
        limit: int = 500,
    ) -> tuple[list[HvacStatus], int]:
        base = select(HvacStatus).where(HvacStatus.building_id == building_id)

        if zone_id:
            base = base.where(HvacStatus.zone_id == zone_id)
        if device_type:
            base = base.where(HvacStatus.device_type == device_type)
        if status_filter:
            base = base.where(HvacStatus.status == status_filter)
        if start:
            base = base.where(HvacStatus.time >= start)
        if end:
            base = base.where(HvacStatus.time <= end)

        count_result = await db.execute(
            select(sa_func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            base.order_by(HvacStatus.time.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total
