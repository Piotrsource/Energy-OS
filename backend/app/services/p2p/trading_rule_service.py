from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.trading_rule import TradingRule
from app.schemas.p2p.trading_rule import TradingRuleCreate, TradingRuleUpdate


class TradingRuleService:

    @staticmethod
    async def create(
        db: AsyncSession, prosumer_id: UUID, data: TradingRuleCreate,
    ) -> TradingRule:
        rule = TradingRule(
            user_id=prosumer_id,
            rule_type=data.rule_type,
            conditions_json=data.conditions_json,
            action_json=data.action_json,
            description=data.description,
            enabled=data.enabled,
        )
        db.add(rule)
        await db.flush()
        return rule

    @staticmethod
    async def list_by_user(
        db: AsyncSession, prosumer_id: UUID,
    ) -> list[TradingRule]:
        result = await db.execute(
            select(TradingRule)
            .where(TradingRule.user_id == prosumer_id)
            .order_by(TradingRule.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, rule_id: UUID) -> TradingRule | None:
        result = await db.execute(
            select(TradingRule).where(TradingRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession, rule_id: UUID, prosumer_id: UUID, data: TradingRuleUpdate,
    ) -> TradingRule | None:
        rule = await TradingRuleService.get_by_id(db, rule_id)
        if not rule or rule.user_id != prosumer_id:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        await db.flush()
        return rule

    @staticmethod
    async def delete(db: AsyncSession, rule_id: UUID, prosumer_id: UUID) -> bool:
        rule = await TradingRuleService.get_by_id(db, rule_id)
        if not rule or rule.user_id != prosumer_id:
            return False
        await db.delete(rule)
        await db.flush()
        return True
