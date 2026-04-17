# =============================================================================
# models/sensor_reading.py — Sensor Reading ORM Model (TimescaleDB Hypertable)
# =============================================================================
# PURPOSE: Stores time-series data from IoT sensors deployed in buildings.
# This is the highest-volume table in the system — a single building with
# 100 sensors reporting every 30 seconds generates ~288,000 rows per day.
#
# TIMESCALEDB HYPERTABLE:
#   This table is converted to a TimescaleDB hypertable by an Alembic migration.
#   Hypertables automatically partition data into time-based chunks (1 day each)
#   for efficient time-range queries and automatic data lifecycle management.
#
# IMPORTANT — COMPOSITE PRIMARY KEY:
#   TimescaleDB requires the time column to be part of any unique constraint.
#   Therefore, we use a composite PK of (time, sensor_id) instead of a
#   single-column UUID primary key. This is a TimescaleDB-specific pattern.
#
# SENSOR TYPES (examples):
#   - "temperature"  → ambient temperature in °C
#   - "humidity"     → relative humidity in %
#   - "co2"          → CO2 concentration in ppm
#   - "occupancy"    → number of people detected
#   - "light_level"  → illumination in lux
#   - "power"        → instantaneous power draw in watts
#
# TABLE: sensor_readings
# COLUMNS: time (PK), sensor_id (PK), building_id (FK), zone_id (FK),
#          sensor_type, value
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SensorReading(Base):
    """
    A single data point from an IoT sensor at a specific moment in time.
    Stored in a TimescaleDB hypertable partitioned by the 'time' column.
    """
    __tablename__ = "sensor_readings"
    __table_args__ = (
        # Composite primary key: TimescaleDB requires 'time' in all unique constraints
        PrimaryKeyConstraint("time", "sensor_id"),
        {"comment": "TimescaleDB hypertable: auto-partitioned by time (1-day chunks)"},
    )

    # -------------------------------------------------------------------------
    # TIME COLUMN — Partitioning dimension for TimescaleDB
    # -------------------------------------------------------------------------
    time: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Timestamp when the sensor reading was captured (UTC)"
    )

    # -------------------------------------------------------------------------
    # SENSOR IDENTIFIER — Part of composite primary key
    # -------------------------------------------------------------------------
    sensor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Unique hardware identifier for the sensor device"
    )

    # -------------------------------------------------------------------------
    # FOREIGN KEYS — Link reading to building and zone
    # -------------------------------------------------------------------------
    building_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buildings.id"),
        nullable=False,
        comment="The building where this sensor is installed"
    )
    zone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("zones.id"),
        nullable=False,
        comment="The zone within the building where this sensor operates"
    )

    # -------------------------------------------------------------------------
    # READING DATA
    # -------------------------------------------------------------------------
    sensor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="What the sensor measures: temperature, humidity, co2, occupancy, etc."
    )
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="The measured value (units depend on sensor_type)"
    )
