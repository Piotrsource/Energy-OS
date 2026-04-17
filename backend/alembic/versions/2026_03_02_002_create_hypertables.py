"""Convert time-series tables to TimescaleDB hypertables

Revision ID: 002_hypertables
Revises: 001_initial
Create Date: 2026-03-02

PURPOSE:
    Convert the three time-series tables (sensor_readings, hvac_status,
    energy_meter) into TimescaleDB hypertables and create optimized indexes.

    WHAT ARE HYPERTABLES?
    Hypertables are TimescaleDB's abstraction over standard PostgreSQL tables.
    They automatically partition data into "chunks" based on time intervals.
    This provides:
        - 10-100x faster time-range queries via chunk exclusion
        - Efficient data retention policies (drop old chunks without VACUUM)
        - Built-in compression for long-term storage
        - time_bucket() function for fast aggregation queries

    CHUNK INTERVAL:
    Each hypertable is configured with 1-day chunks. This means data for
    each day is stored in a separate physical partition. For ~200-300 sensor
    writes/second, 1-day chunks balance query performance with chunk overhead.

    INDEXES:
    Custom indexes are created for the most common query patterns:
        - (building_id, time DESC): "Show me all readings for this building"
        - (zone_id, time DESC): "Show me all readings for this zone"
    The DESC ordering on time makes recent-data queries faster.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002_hypertables"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # CONVERT TABLES TO HYPERTABLES
    # =========================================================================
    # create_hypertable() transforms a regular table into a TimescaleDB
    # hypertable. The 'time' column becomes the partitioning dimension.
    # chunk_time_interval sets how much time data each chunk (partition) holds.
    # if_not_exists prevents errors if the table is already a hypertable.
    # =========================================================================

    # --- Sensor Readings ---
    # Highest-volume table. 100 sensors × 1 reading/30s = 288,000 rows/day/building
    op.execute(
        "SELECT create_hypertable('sensor_readings', 'time', "
        "chunk_time_interval => INTERVAL '1 day', "
        "if_not_exists => TRUE);"
    )

    # --- HVAC Status ---
    # Lower volume than sensors but still needs time-based partitioning
    # for efficient status history queries.
    op.execute(
        "SELECT create_hypertable('hvac_status', 'time', "
        "chunk_time_interval => INTERVAL '1 day', "
        "if_not_exists => TRUE);"
    )

    # --- Energy Meter ---
    # Medium volume. Typically 1 reading per meter per 15 minutes.
    # Powers the energy summary and carbon emissions analytics.
    op.execute(
        "SELECT create_hypertable('energy_meter', 'time', "
        "chunk_time_interval => INTERVAL '1 day', "
        "if_not_exists => TRUE);"
    )

    # =========================================================================
    # CREATE OPTIMIZED INDEXES
    # =========================================================================
    # These indexes support the most common query patterns in the API.
    # TimescaleDB automatically creates an index on (time) for each hypertable,
    # but we need compound indexes for filtered queries.
    # =========================================================================

    # Sensor Readings indexes
    # Query: "Get temperature readings for building X in the last 24 hours"
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_sensor_readings_building_time "
        "ON sensor_readings (building_id, time DESC);"
    )
    # Query: "Get all sensor readings for zone Y between date A and date B"
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_sensor_readings_zone_time "
        "ON sensor_readings (zone_id, time DESC);"
    )

    # HVAC Status indexes
    # Query: "Show HVAC status for building X over the last week"
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_hvac_status_building_time "
        "ON hvac_status (building_id, time DESC);"
    )

    # Energy Meter indexes
    # Query: "Calculate energy summary for building X between start and end dates"
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_energy_meter_building_time "
        "ON energy_meter (building_id, time DESC);"
    )


def downgrade() -> None:
    # Drop the custom indexes (hypertable conversion cannot be undone without
    # dropping and recreating the table, which is handled by migration 001's downgrade)
    op.execute("DROP INDEX IF EXISTS idx_energy_meter_building_time;")
    op.execute("DROP INDEX IF EXISTS idx_hvac_status_building_time;")
    op.execute("DROP INDEX IF EXISTS idx_sensor_readings_zone_time;")
    op.execute("DROP INDEX IF EXISTS idx_sensor_readings_building_time;")
