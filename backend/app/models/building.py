# =============================================================================
# models/building.py — Building ORM Model
# =============================================================================
# PURPOSE: Represents a physical building (hotel, office, retail, etc.) in the
# database. Buildings are the top-level entity in the platform's hierarchy:
#
#   Building → Zones → Sensors / Forecasts / Recommendations
#
# Every zone, user, and sensor reading is associated with a building.
# A single platform installation can manage hundreds of buildings.
#
# TABLE: buildings
# COLUMNS: id (UUID PK), name, address, type, timezone
# RELATIONSHIPS: zones (one-to-many), users (one-to-many)
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Building(Base):
    """
    A physical building managed by the energy optimization platform.

    Examples: "Marriott Downtown", "TechCorp HQ", "Retail Center West"
    """
    __tablename__ = "buildings"

    # -------------------------------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------------------------------
    # UUIDs instead of auto-increment integers for:
    #   - Safe generation across distributed systems (no sequence conflicts)
    #   - No information leakage (can't guess building count from IDs)
    # -------------------------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique building identifier (UUID v4)"
    )

    # -------------------------------------------------------------------------
    # BUILDING ATTRIBUTES
    # -------------------------------------------------------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable building name, e.g. 'Marriott Downtown'"
    )
    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full street address of the building"
    )
    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Building type: hotel, office, retail, hospital, etc."
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UTC",
        comment="IANA timezone identifier, e.g. 'America/New_York', 'Europe/Warsaw'"
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
    zones = relationship("Zone", back_populates="building", cascade="all, delete-orphan")
    users = relationship("User", back_populates="building")
