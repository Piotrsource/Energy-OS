# =============================================================================
# services/sensor_service.py — Sensor Data Business Logic
# =============================================================================
# PURPOSE: Handle sensor reading ingestion (bulk insert) and time-range queries.
# This is the highest-throughput service — it must handle ~200-300 writes/sec.
#
# METHODS:
#   bulk_insert()      → Insert multiple sensor readings at once
#   query_readings()   → Retrieve readings with time-range and filter support
#
# TIMESCALEDB OPTIMIZATION:
#   Time-range queries on hypertables benefit from chunk exclusion — TimescaleDB
#   automatically skips chunks (partitions) that don't overlap the query range.
#   This means querying "last 1 hour" on a table with years of data is fast.
# =============================================================================

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sensor_reading import SensorReading
from app.schemas.sensor import SensorReadingCreate

logger = logging.getLogger("energy_platform")


class SensorService:
    """Static methods for sensor data ingestion and retrieval."""

    @staticmethod
    async def bulk_insert(
        db: AsyncSession, readings: list[SensorReadingCreate]
    ) -> int:
        objects = [SensorReading(**r.model_dump()) for r in readings]
        db.add_all(objects)
        await db.flush()

        try:
            from app.services.realtime_service import RealtimeService
            for r in readings:
                reading_dict = {
                    "time": r.time.isoformat(),
                    "sensor_id": r.sensor_id,
                    "building_id": str(r.building_id),
                    "zone_id": str(r.zone_id),
                    "sensor_type": r.sensor_type,
                    "value": r.value,
                }
                await RealtimeService.cache_reading(r.sensor_id, str(r.building_id), reading_dict)
                await RealtimeService.publish_reading(str(r.building_id), reading_dict)
        except Exception:
            logger.warning("Failed to publish readings to Redis (non-fatal)", exc_info=True)

        return len(objects)

    @staticmethod
    async def query_readings(
        db: AsyncSession,
        building_id: UUID,
        zone_id: UUID | None = None,
        sensor_type: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 0,
        limit: int = 500,
    ) -> tuple[list[SensorReading], int]:
        base = select(SensorReading).where(SensorReading.building_id == building_id)

        if zone_id:
            base = base.where(SensorReading.zone_id == zone_id)
        if sensor_type:
            base = base.where(SensorReading.sensor_type == sensor_type)
        if start:
            base = base.where(SensorReading.time >= start)
        if end:
            base = base.where(SensorReading.time <= end)

        count_result = await db.execute(
            select(sa_func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            base.order_by(SensorReading.time.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total
