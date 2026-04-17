# =============================================================================
# services/building_service.py — Building Business Logic
# =============================================================================
# PURPOSE: Encapsulate all database operations for buildings.
# Routers call these methods instead of writing SQL directly.
#
# METHODS:
#   list_all()   → Get all buildings
#   get_by_id()  → Get one building by UUID
#   create()     → Insert a new building
#   update()     → Partial update (only provided fields)
#   delete()     → Remove a building and cascade to zones
# =============================================================================

from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.schemas.building import BuildingCreate, BuildingUpdate


class BuildingService:
    """Static methods for building CRUD operations."""

    @staticmethod
    async def list_all(
        db: AsyncSession, *, offset: int = 0, limit: int = 50
    ) -> tuple[list[Building], int]:
        count_result = await db.execute(select(sa_func.count()).select_from(Building))
        total = count_result.scalar_one()

        result = await db.execute(
            select(Building).order_by(Building.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_by_id(db: AsyncSession, building_id: UUID) -> Building | None:
        """
        Retrieve a single building by its UUID.
        Returns None if the building does not exist.
        """
        result = await db.execute(
            select(Building).where(Building.id == building_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: BuildingCreate) -> Building:
        """
        Create a new building from the provided data.
        Uses flush() instead of commit() — the session dependency handles commit.
        """
        building = Building(**data.model_dump())
        db.add(building)
        await db.flush()   # Assigns the UUID without committing the transaction
        return building

    @staticmethod
    async def update(
        db: AsyncSession, building_id: UUID, data: BuildingUpdate
    ) -> Building | None:
        """
        Partially update a building. Only fields present in the request are changed.
        Returns the updated building, or None if not found.
        """
        building = await BuildingService.get_by_id(db, building_id)
        if not building:
            return None

        # exclude_unset=True: only update fields the client explicitly sent
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(building, field, value)

        await db.flush()
        await db.refresh(building)
        return building

    @staticmethod
    async def delete(db: AsyncSession, building_id: UUID) -> bool:
        """
        Delete a building by UUID. Cascades to zones due to FK constraint.
        Returns True if deleted, False if building was not found.
        """
        building = await BuildingService.get_by_id(db, building_id)
        if not building:
            return False
        await db.delete(building)
        await db.flush()
        return True
