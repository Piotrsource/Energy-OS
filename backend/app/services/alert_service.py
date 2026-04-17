from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert


class AlertService:
    @staticmethod
    async def list_by_building(
        db: AsyncSession, building_id: UUID, *, acknowledged: bool | None = None,
        offset: int = 0, limit: int = 50
    ) -> tuple[list[Alert], int]:
        from app.models.alert_rule import AlertRule
        base = (
            select(Alert)
            .join(AlertRule, Alert.rule_id == AlertRule.id)
            .where(AlertRule.building_id == building_id)
        )
        if acknowledged is True:
            base = base.where(Alert.acknowledged_at.is_not(None))
        elif acknowledged is False:
            base = base.where(Alert.acknowledged_at.is_(None))

        count_result = await db.execute(select(sa_func.count()).select_from(base.subquery()))
        total = count_result.scalar_one()
        result = await db.execute(base.order_by(Alert.triggered_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all()), total

    @staticmethod
    async def acknowledge(db: AsyncSession, alert_id: UUID, user_id: UUID) -> Alert | None:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            return None
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by = user_id
        await db.flush()
        return alert

    @staticmethod
    async def create(db: AsyncSession, rule_id: UUID, sensor_id: str, value: float) -> Alert:
        alert = Alert(rule_id=rule_id, sensor_id=sensor_id, value=value)
        db.add(alert)
        await db.flush()
        return alert
