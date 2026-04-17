from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


class NotificationService:
    @staticmethod
    async def list_for_user(
        db: AsyncSession, user_id: UUID, *, unread_only: bool = False,
        offset: int = 0, limit: int = 50
    ) -> tuple[list[Notification], int]:
        base = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            base = base.where(Notification.read_at.is_(None))
        count_result = await db.execute(select(sa_func.count()).select_from(base.subquery()))
        total = count_result.scalar_one()
        result = await db.execute(base.order_by(Notification.sent_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all()), total

    @staticmethod
    async def mark_read(db: AsyncSession, notification_id: UUID, user_id: UUID) -> Notification | None:
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        notif = result.scalar_one_or_none()
        if not notif:
            return None
        notif.read_at = datetime.now(timezone.utc)
        await db.flush()
        return notif

    @staticmethod
    async def create_for_alert(
        db: AsyncSession, user_id: UUID, alert_id: UUID, title: str, body: str
    ) -> Notification:
        notif = Notification(user_id=user_id, alert_id=alert_id, title=title, body=body)
        db.add(notif)
        await db.flush()
        return notif

    @staticmethod
    async def unread_count(db: AsyncSession, user_id: UUID) -> int:
        result = await db.execute(
            select(sa_func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        )
        return result.scalar_one()
