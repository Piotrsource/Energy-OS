from uuid import UUID
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert_rule import AlertRule
from app.schemas.alert_rule import AlertRuleCreate, AlertRuleUpdate


class AlertRuleService:
    @staticmethod
    async def list_by_building(
        db: AsyncSession, building_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> tuple[list[AlertRule], int]:
        base = select(AlertRule).where(AlertRule.building_id == building_id)
        count_result = await db.execute(select(sa_func.count()).select_from(base.subquery()))
        total = count_result.scalar_one()
        result = await db.execute(base.order_by(AlertRule.created_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all()), total

    @staticmethod
    async def get_by_id(db: AsyncSession, rule_id: UUID) -> AlertRule | None:
        result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: AlertRuleCreate) -> AlertRule:
        rule = AlertRule(**data.model_dump())
        db.add(rule)
        await db.flush()
        return rule

    @staticmethod
    async def update(db: AsyncSession, rule_id: UUID, data: AlertRuleUpdate) -> AlertRule | None:
        rule = await AlertRuleService.get_by_id(db, rule_id)
        if not rule:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        await db.flush()
        return rule

    @staticmethod
    async def delete(db: AsyncSession, rule_id: UUID) -> bool:
        rule = await AlertRuleService.get_by_id(db, rule_id)
        if not rule:
            return False
        await db.delete(rule)
        await db.flush()
        return True

    @staticmethod
    async def get_enabled_rules(db: AsyncSession) -> list[AlertRule]:
        result = await db.execute(select(AlertRule).where(AlertRule.enabled == True))
        return list(result.scalars().all())
