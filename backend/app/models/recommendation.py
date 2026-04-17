# =============================================================================
# models/recommendation.py — Recommendation ORM Model
# =============================================================================
# PURPOSE: Stores AI-generated optimization recommendations that suggest
# specific actions to reduce energy consumption while maintaining comfort.
#
# Recommendations go through a lifecycle:
#   pending → approved → applied   (happy path)
#   pending → rejected             (user overrides AI suggestion)
#
# RECOMMENDATION TYPES (examples):
#   - "hvac_setpoint"     → adjust thermostat to a specific temperature
#   - "lighting_level"    → dim/brighten lights to a percentage
#   - "hvac_schedule"     → shift HVAC start time
#   - "ventilation_rate"  → adjust fresh air intake
#
# The value field stores the recommended numeric setting (e.g., 22.5 for
# temperature in °C, or 75 for lighting at 75%).
#
# TABLE: recommendations
# COLUMNS: id (UUID PK), zone_id (FK), recommendation_type, value, status,
#          created_at, applied_at
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Recommendation(Base):
    """
    An AI-generated optimization action for a specific zone.
    """
    __tablename__ = "recommendations"

    # -------------------------------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique recommendation identifier"
    )

    # -------------------------------------------------------------------------
    # FOREIGN KEY — Which zone this recommendation targets
    # -------------------------------------------------------------------------
    zone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False,
        comment="The zone this recommendation targets"
    )

    # -------------------------------------------------------------------------
    # RECOMMENDATION DATA
    # -------------------------------------------------------------------------
    recommendation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of recommendation: hvac_setpoint, lighting_level, hvac_schedule, etc."
    )
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Recommended value (units depend on type, e.g., °C for setpoint, % for lighting)"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Lifecycle status: pending, approved, applied, rejected"
    )

    # -------------------------------------------------------------------------
    # TIMESTAMPS
    # -------------------------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="When the AI engine generated this recommendation"
    )
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="When the recommendation was applied to the BMS/HVAC system (null if not yet applied)"
    )

    # -------------------------------------------------------------------------
    # RELATIONSHIPS
    # -------------------------------------------------------------------------
    zone = relationship("Zone", back_populates="recommendations")
