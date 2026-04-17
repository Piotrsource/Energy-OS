import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NotificationPreference(Base):
    """
    Per-user notification preferences.

    Controls which channels are enabled and the minimum severity level
    a notification must have before it is delivered through that channel.
    """
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True,
    )

    # Channel toggles
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    # Minimum severity to trigger a notification ("low" means everything gets through)
    min_severity: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="low",
        comment="Minimum severity to notify: low, medium, high, critical",
    )

    # Optional email override (defaults to user.email if blank)
    email_address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Quiet hours (UTC) — suppress non-critical notifications
    quiet_start_hour: Mapped[int | None] = mapped_column(nullable=True, comment="Start of quiet hours (0-23 UTC)")
    quiet_end_hour: Mapped[int | None] = mapped_column(nullable=True, comment="End of quiet hours (0-23 UTC)")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )
