# =============================================================================
# services/forecast_service.py — Forecast Business Logic
# =============================================================================
# PURPOSE: Handle AI forecast storage and retrieval.
# Forecasts are created by the ML pipeline and queried by the dashboard.
#
# METHODS:
#   create()              → Insert a single forecast
#   list_by_building()    → Get forecasts for all zones in a building
# =============================================================================

from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecast import Forecast
from app.models.zone import Zone
from app.schemas.forecast import ForecastCreate


class ForecastService:
    """Static methods for forecast CRUD operations."""

    @staticmethod
    async def create(db: AsyncSession, data: ForecastCreate) -> Forecast:
        forecast = Forecast(**data.model_dump())
        db.add(forecast)
        await db.flush()
        return forecast

    @staticmethod
    async def list_by_building(
        db: AsyncSession, building_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> tuple[list[Forecast], int]:
        base = (
            select(Forecast)
            .join(Zone, Forecast.zone_id == Zone.id)
            .where(Zone.building_id == building_id)
        )

        count_result = await db.execute(
            select(sa_func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            base.order_by(Forecast.forecast_time.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total
