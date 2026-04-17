from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_preference import NotificationPreference


# Severity ordering for threshold comparison
SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class NotificationPreferenceService:
    @staticmethod
    async def get_or_create(db: AsyncSession, user_id: UUID) -> NotificationPreference:
        """Get preferences for a user, creating defaults if none exist."""
        result = await db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            pref = NotificationPreference(user_id=user_id)
            db.add(pref)
            await db.flush()
        return pref

    @staticmethod
    async def update(
        db: AsyncSession, user_id: UUID, updates: dict,
    ) -> NotificationPreference:
        """Update notification preferences for a user."""
        pref = await NotificationPreferenceService.get_or_create(db, user_id)
        for key, value in updates.items():
            if value is not None and hasattr(pref, key):
                setattr(pref, key, value)
        await db.flush()
        return pref

    @staticmethod
    def passes_severity_filter(alert_severity: str, min_severity: str) -> bool:
        """Return True if the alert severity meets or exceeds the minimum."""
        return SEVERITY_ORDER.get(alert_severity, 0) >= SEVERITY_ORDER.get(min_severity, 0)

    @staticmethod
    def is_quiet_hours(current_hour_utc: int, quiet_start: int | None, quiet_end: int | None) -> bool:
        """Return True if the current UTC hour falls within quiet hours."""
        if quiet_start is None or quiet_end is None:
            return False
        if quiet_start <= quiet_end:
            return quiet_start <= current_hour_utc < quiet_end
        # Wraps midnight, e.g., 22 -> 6
        return current_hour_utc >= quiet_start or current_hour_utc < quiet_end
