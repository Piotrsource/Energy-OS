from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.energy_community import EnergyCommunity
from app.models.p2p.community_member import CommunityMember, CommunityRole
from app.models.p2p.p2p_order import P2POrder, OrderStatus
from app.schemas.p2p.community import CommunityCreate, CommunityDashboard


class CommunityService:

    @staticmethod
    async def create(
        db: AsyncSession, creator_id: UUID, data: CommunityCreate,
    ) -> EnergyCommunity:
        community = EnergyCommunity(
            name=data.name,
            description=data.description,
            location_lat=data.location_lat,
            location_lng=data.location_lng,
            radius_km=data.radius_km,
            fee_discount_pct=data.fee_discount_pct,
            created_by=creator_id,
        )
        db.add(community)
        await db.flush()

        member = CommunityMember(
            community_id=community.id,
            user_id=creator_id,
            role=CommunityRole.ADMIN,
        )
        db.add(member)
        await db.flush()
        return community

    @staticmethod
    async def list_all(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[EnergyCommunity]:
        result = await db.execute(
            select(EnergyCommunity)
            .order_by(EnergyCommunity.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, community_id: UUID) -> EnergyCommunity | None:
        result = await db.execute(
            select(EnergyCommunity).where(EnergyCommunity.id == community_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def join(db: AsyncSession, community_id: UUID, user_id: UUID) -> CommunityMember:
        member = CommunityMember(
            community_id=community_id,
            user_id=user_id,
            role=CommunityRole.MEMBER,
        )
        db.add(member)
        await db.flush()
        return member

    @staticmethod
    async def get_members(
        db: AsyncSession, community_id: UUID,
    ) -> list[CommunityMember]:
        result = await db.execute(
            select(CommunityMember).where(CommunityMember.community_id == community_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_member_count(db: AsyncSession, community_id: UUID) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(CommunityMember)
            .where(CommunityMember.community_id == community_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_dashboard(db: AsyncSession, community_id: UUID) -> CommunityDashboard:
        community = await CommunityService.get_by_id(db, community_id)
        if not community:
            raise ValueError("Community not found")

        member_count = await CommunityService.get_member_count(db, community_id)

        members_result = await db.execute(
            select(CommunityMember.user_id)
            .where(CommunityMember.community_id == community_id)
        )
        member_ids = [row[0] for row in members_result.all()]

        total_trades = 0
        total_wh = 0
        total_value = 0

        if member_ids:
            trades = await db.execute(
                select(
                    func.count(),
                    func.coalesce(func.sum(P2POrder.matched_wh), 0),
                    func.coalesce(
                        func.sum(P2POrder.matched_wh * P2POrder.price_cents_per_kwh / 1000),
                        0,
                    ),
                )
                .where(
                    P2POrder.status.in_([OrderStatus.SETTLED, OrderStatus.SETTLING]),
                    P2POrder.seller_id.in_(member_ids) | P2POrder.buyer_id.in_(member_ids),
                )
            )
            row = trades.one()
            total_trades = row[0] or 0
            total_wh = row[1] or 0
            total_value = int(row[2] or 0)

        avg_price = (total_value * 1000 / total_wh) if total_wh > 0 else 0.0
        co2_per_kwh = 0.4  # kg CO2 per kWh avoided by local solar
        co2_avoided = (total_wh / 1000) * co2_per_kwh

        return CommunityDashboard(
            community_id=community.id,
            community_name=community.name,
            member_count=member_count,
            total_trades=total_trades,
            total_kwh_traded=round(total_wh / 1000, 2),
            total_value_cents=total_value,
            avg_price_cents_per_kwh=round(avg_price, 1),
            grid_independence_pct=0.0,
            co2_avoided_kg=round(co2_avoided, 2),
        )
