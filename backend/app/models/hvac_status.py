# =============================================================================
# models/hvac_status.py — HVAC Status ORM Model (TimescaleDB Hypertable)
# =============================================================================
# PURPOSE: Tracks the operational state of HVAC (Heating, Ventilation, and
# Air Conditioning) equipment over time. This data is used to:
#   - Monitor whether equipment is running correctly
#   - Detect anomalies (e.g., HVAC running when building is unoccupied)
#   - Compare actual setpoints against AI recommendations
#   - Calculate equipment runtime hours for maintenance scheduling
#
# DEVICE TYPES (examples):
#   - "ahu"       → Air Handling Unit
#   - "chiller"   → Chiller/cooling plant
#   - "boiler"    → Heating boiler
#   - "fcu"       → Fan Coil Unit
#   - "vav"       → Variable Air Volume box
#
# STATUS VALUES (examples):
#   - "running", "idle", "off", "fault", "maintenance"
#
# TABLE: hvac_status
# COLUMNS: time (PK), device_id (PK), building_id (FK), zone_id (FK),
#          device_type, status, setpoint
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HvacStatus(Base):
    """
    A snapshot of an HVAC device's state at a specific moment in time.
    Stored in a TimescaleDB hypertable partitioned by the 'time' column.
    """
    __tablename__ = "hvac_status"
    __table_args__ = (
        PrimaryKeyConstraint("time", "device_id"),
        {"comment": "TimescaleDB hypertable: auto-partitioned by time (1-day chunks)"},
    )

    # -------------------------------------------------------------------------
    # TIME COLUMN — Partitioning dimension for TimescaleDB
    # -------------------------------------------------------------------------
    time: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Timestamp of this status snapshot (UTC)"
    )

    # -------------------------------------------------------------------------
    # DEVICE IDENTIFIER — Part of composite primary key
    # -------------------------------------------------------------------------
    device_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Unique hardware identifier for the HVAC device"
    )

    # -------------------------------------------------------------------------
    # FOREIGN KEYS — Link status to building and zone
    # -------------------------------------------------------------------------
    building_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buildings.id"),
        nullable=False,
        comment="The building where this HVAC device is installed"
    )
    zone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("zones.id"),
        nullable=False,
        comment="The zone this HVAC device serves"
    )

    # -------------------------------------------------------------------------
    # DEVICE DATA
    # -------------------------------------------------------------------------
    device_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of HVAC equipment: ahu, chiller, boiler, fcu, vav"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Current operational status: running, idle, off, fault, maintenance"
    )
    setpoint: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Current temperature setpoint in °C (null if device has no setpoint)"
    )
