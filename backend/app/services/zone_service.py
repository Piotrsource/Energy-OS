# =============================================================================
# services/zone_service.py — Zone Business Logic
# =============================================================================
# PURPOSE: Encapsulate all database operations for zones.
#
# METHODS:
#   list_by_building() → Get all zones for a specific building
#   get_by_id()        → Get one zone by UUID
#   create()           → Insert a new zone
# =============================================================================

from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.zone import Zone
from app.schemas.zone import ZoneCreate


class ZoneService:
    """Static methods for zone CRUD operations."""

    @staticmethod
    async def list_by_building(
        db: AsyncSession, building_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> tuple[list[Zone], int]:
        base = select(Zone).where(Zone.building_id == building_id)

        count_result = await db.execute(
            select(sa_func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            base.order_by(Zone.floor, Zone.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_by_id(db: AsyncSession, zone_id: UUID) -> Zone | None:
        """
        Retrieve a single zone by its UUID.
        Returns None if the zone does not exist.
        """
        result = await db.execute(
            select(Zone).where(Zone.id == zone_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: ZoneCreate) -> Zone:
        """
        Create a new zone from the provided data.
        The building_id must reference an existing building.
        """
        zone = Zone(**data.model_dump())
        db.add(zone)
        await db.flush()
        return zone
