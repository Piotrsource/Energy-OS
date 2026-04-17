# =============================================================================
# models/zone.py — Zone ORM Model
# =============================================================================
# PURPOSE: Represents a distinct area within a building (floor, wing, room,
# conference area, etc.). Zones are the primary granularity at which the AI
# engine generates forecasts and optimization recommendations.
#
# HIERARCHY: Building → Zone → Sensors / Forecasts / Recommendations
#
# EXAMPLES:
#   - Hotel: "Floor 3", "Lobby", "Restaurant", "Pool Area"
#   - Office: "East Wing Floor 5", "Server Room", "Conference Suite A"
#
# TABLE: zones
# COLUMNS: id (UUID PK), building_id (FK), name, floor
# RELATIONSHIPS: building (many-to-one), forecasts, recommendations
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Zone(Base):
    """
    A distinct area within a building where sensors operate and
    energy optimization decisions are made.
    """
    __tablename__ = "zones"

    # -------------------------------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique zone identifier (UUID v4)"
    )

    # -------------------------------------------------------------------------
    # FOREIGN KEY — Links this zone to its parent building
    # -------------------------------------------------------------------------
    building_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        comment="The building this zone belongs to"
    )

    # -------------------------------------------------------------------------
    # ZONE ATTRIBUTES
    # -------------------------------------------------------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Zone name, e.g. 'Floor 3 East Wing', 'Lobby'"
    )
    floor: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Floor number within the building (nullable for zones spanning multiple floors)"
    )

    # -------------------------------------------------------------------------
    # TIMESTAMPS (Phase 1)
    # -------------------------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # -------------------------------------------------------------------------
    # RELATIONSHIPS
    # -------------------------------------------------------------------------
    building = relationship("Building", back_populates="zones")
    forecasts = relationship("Forecast", back_populates="zone", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="zone", cascade="all, delete-orphan")
