# =============================================================================
# models/energy_meter.py — Energy Meter ORM Model (TimescaleDB Hypertable)
# =============================================================================
# PURPOSE: Stores electrical energy consumption data from building meters.
# This data powers the analytics dashboard (energy summary, carbon emissions)
# and feeds the AI engine for consumption forecasting.
#
# Each row represents a snapshot from an energy meter at a specific time,
# recording cumulative kWh and instantaneous electrical measurements.
#
# METER TYPES (by convention, stored as meter_id prefix):
#   - "main-*"    → Whole-building main meter
#   - "hvac-*"    → Sub-meter for HVAC systems
#   - "light-*"   → Sub-meter for lighting circuits
#   - "plug-*"    → Sub-meter for plug loads (outlets)
#
# TABLE: energy_meter
# COLUMNS: time (PK), meter_id (PK), building_id (FK), kwh, voltage, current
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EnergyMeter(Base):
    """
    A snapshot of energy meter readings at a specific moment in time.
    Stored in a TimescaleDB hypertable partitioned by the 'time' column.
    """
    __tablename__ = "energy_meter"
    __table_args__ = (
        PrimaryKeyConstraint("time", "meter_id"),
        {"comment": "TimescaleDB hypertable: auto-partitioned by time (1-day chunks)"},
    )

    # -------------------------------------------------------------------------
    # TIME COLUMN — Partitioning dimension for TimescaleDB
    # -------------------------------------------------------------------------
    time: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Timestamp of the meter reading (UTC)"
    )

    # -------------------------------------------------------------------------
    # METER IDENTIFIER — Part of composite primary key
    # -------------------------------------------------------------------------
    meter_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Unique identifier for the energy meter"
    )

    # -------------------------------------------------------------------------
    # FOREIGN KEY — Link meter reading to a building
    # -------------------------------------------------------------------------
    building_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buildings.id"),
        nullable=False,
        comment="The building where this meter is installed"
    )

    # -------------------------------------------------------------------------
    # METER DATA
    # -------------------------------------------------------------------------
    kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Energy consumed in kilowatt-hours since last reading"
    )
    voltage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Instantaneous voltage in volts (null if meter doesn't measure this)"
    )
    current: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Instantaneous current in amperes (null if meter doesn't measure this)"
    )
