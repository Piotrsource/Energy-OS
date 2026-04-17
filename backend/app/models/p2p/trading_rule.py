import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RuleType(str, enum.Enum):
    AUTO_SELL = "auto_sell"
    AUTO_BUY = "auto_buy"


class TradingRule(Base):
    """
    User-configured automation rules evaluated every 15 minutes.
    Example: 'Sell excess above 80% battery at >= 12c/kWh between 4-8 PM.'
    conditions_json and action_json store the rule logic as structured JSON.
    """
    __tablename__ = "trading_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_type: Mapped[RuleType] = mapped_column(
        Enum(RuleType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    conditions_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    action_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    prosumer = relationship("ProsumerProfile", backref="trading_rules")
