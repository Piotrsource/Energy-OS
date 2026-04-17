# =============================================================================
# services/recommendation_service.py — Recommendation Business Logic
# =============================================================================
# PURPOSE: Handle AI recommendation storage, retrieval, and lifecycle updates.
#
# LIFECYCLE: pending → approved → applied (or rejected at any stage)
#
# METHODS:
#   create()              → Insert a new recommendation (status: pending)
#   list_by_building()    → Get recommendations for all zones in a building
#   update_status()       → Change recommendation status (approve/apply/reject)
# =============================================================================

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.models.zone import Zone
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate


class RecommendationService:
    """Static methods for recommendation CRUD and lifecycle operations."""

    @staticmethod
    async def create(db: AsyncSession, data: RecommendationCreate) -> Recommendation:
        recommendation = Recommendation(**data.model_dump())
        db.add(recommendation)
        await db.flush()
        return recommendation

    @staticmethod
    async def list_by_building(
        db: AsyncSession, building_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> tuple[list[Recommendation], int]:
        base = (
            select(Recommendation)
            .join(Zone, Recommendation.zone_id == Zone.id)
            .where(Zone.building_id == building_id)
        )

        count_result = await db.execute(
            select(sa_func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            base.order_by(Recommendation.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def update_status(
        db: AsyncSession,
        recommendation_id: UUID,
        data: RecommendationUpdate,
    ) -> Recommendation | None:
        """
        Update a recommendation's lifecycle status.

        Valid transitions:
            pending → approved, rejected
            approved → applied, rejected
            applied → (terminal state, no further transitions)
            rejected → (terminal state, no further transitions)

        If status is set to "applied" and no applied_at is provided,
        the current UTC timestamp is automatically used.
        """
        result = await db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        recommendation = result.scalar_one_or_none()
        if not recommendation:
            return None

        recommendation.status = data.status

        # Auto-set applied_at when status changes to "applied"
        if data.status == "applied":
            recommendation.applied_at = data.applied_at or datetime.now(timezone.utc)
        elif data.applied_at:
            recommendation.applied_at = data.applied_at

        await db.flush()
        return recommendation
