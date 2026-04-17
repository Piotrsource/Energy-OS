"""Initial schema — create all tables

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-02

PURPOSE:
    Creates all database tables for the AI Energy Optimization Platform.

    RELATIONAL TABLES (standard PostgreSQL):
        - buildings:        Top-level entity for physical buildings
        - zones:            Areas within buildings (floors, wings, rooms)
        - users:            Platform operators with role-based access
        - forecasts:        AI-generated predictions per zone
        - recommendations:  AI-generated optimization actions per zone

    TIME-SERIES TABLES (will become TimescaleDB hypertables in migration 002):
        - sensor_readings:  IoT sensor data (temperature, humidity, CO2, etc.)
        - hvac_status:      HVAC equipment operational state over time
        - energy_meter:     Electrical energy consumption readings

    All relational tables use UUID primary keys for distributed safety.
    Time-series tables use composite PKs (time + device/sensor ID) as
    required by TimescaleDB's hypertable constraints.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # BUILDINGS TABLE
    # =========================================================================
    # Top-level entity. Every zone, user, and sensor reading belongs to a building.
    # =========================================================================
    op.create_table(
        "buildings",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique building identifier (UUID v4)"),
        sa.Column("name", sa.String(255), nullable=False, comment="Human-readable building name"),
        sa.Column("address", sa.Text(), nullable=False, comment="Full street address"),
        sa.Column("type", sa.String(100), nullable=False, comment="Building type: hotel, office, retail, etc."),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC", comment="IANA timezone identifier"),
        sa.PrimaryKeyConstraint("id"),
    )

    # =========================================================================
    # ZONES TABLE
    # =========================================================================
    # Subdivisions within a building. Zones are the granularity for AI predictions.
    # =========================================================================
    op.create_table(
        "zones",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique zone identifier"),
        sa.Column("building_id", sa.Uuid(), nullable=False, comment="Parent building FK"),
        sa.Column("name", sa.String(255), nullable=False, comment="Zone name"),
        sa.Column("floor", sa.Integer(), nullable=True, comment="Floor number"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"], ondelete="CASCADE"),
    )

    # =========================================================================
    # USERS TABLE
    # =========================================================================
    # Platform operators with authentication and role-based access control.
    # The email column is indexed for fast login lookups.
    # =========================================================================
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique user identifier"),
        sa.Column("building_id", sa.Uuid(), nullable=False, comment="Primary building FK"),
        sa.Column("name", sa.String(255), nullable=False, comment="Full name"),
        sa.Column("email", sa.String(255), nullable=False, comment="Email (unique, used for login)"),
        sa.Column("role", sa.Enum("admin", "facility_manager", "technician", name="userrole"), nullable=False, comment="Access role"),
        sa.Column("password_hash", sa.String(255), nullable=False, comment="bcrypt hash"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # =========================================================================
    # FORECASTS TABLE
    # =========================================================================
    # AI-generated predictions stored per zone and future timestamp.
    # =========================================================================
    op.create_table(
        "forecasts",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique forecast identifier"),
        sa.Column("zone_id", sa.Uuid(), nullable=False, comment="Target zone FK"),
        sa.Column("forecast_type", sa.String(50), nullable=False, comment="Prediction type"),
        sa.Column("predicted_value", sa.Float(), nullable=False, comment="Predicted value"),
        sa.Column("forecast_time", sa.DateTime(timezone=True), nullable=False, comment="Future time predicted"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), comment="When generated"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
    )

    # =========================================================================
    # RECOMMENDATIONS TABLE
    # =========================================================================
    # AI-generated optimization actions with a lifecycle (pending → applied/rejected).
    # =========================================================================
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique recommendation identifier"),
        sa.Column("zone_id", sa.Uuid(), nullable=False, comment="Target zone FK"),
        sa.Column("recommendation_type", sa.String(50), nullable=False, comment="Action type"),
        sa.Column("value", sa.Float(), nullable=False, comment="Recommended value"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", comment="Lifecycle status"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), comment="When generated"),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True, comment="When applied (null if not yet)"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
    )

    # =========================================================================
    # SENSOR READINGS TABLE (becomes hypertable in migration 002)
    # =========================================================================
    # High-volume IoT sensor data. Composite PK (time, sensor_id) required
    # by TimescaleDB for hypertable conversion.
    # =========================================================================
    op.create_table(
        "sensor_readings",
        sa.Column("time", sa.DateTime(), nullable=False, comment="Reading timestamp (UTC)"),
        sa.Column("sensor_id", sa.String(100), nullable=False, comment="Sensor hardware ID"),
        sa.Column("building_id", sa.Uuid(), nullable=False, comment="Building FK"),
        sa.Column("zone_id", sa.Uuid(), nullable=False, comment="Zone FK"),
        sa.Column("sensor_type", sa.String(50), nullable=False, comment="Measurement type"),
        sa.Column("value", sa.Float(), nullable=False, comment="Measured value"),
        sa.PrimaryKeyConstraint("time", "sensor_id"),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
    )

    # =========================================================================
    # HVAC STATUS TABLE (becomes hypertable in migration 002)
    # =========================================================================
    # Tracks HVAC equipment state over time for monitoring and anomaly detection.
    # =========================================================================
    op.create_table(
        "hvac_status",
        sa.Column("time", sa.DateTime(), nullable=False, comment="Status timestamp (UTC)"),
        sa.Column("device_id", sa.String(100), nullable=False, comment="HVAC device ID"),
        sa.Column("building_id", sa.Uuid(), nullable=False, comment="Building FK"),
        sa.Column("zone_id", sa.Uuid(), nullable=False, comment="Zone FK"),
        sa.Column("device_type", sa.String(50), nullable=False, comment="HVAC equipment type"),
        sa.Column("status", sa.String(50), nullable=False, comment="Operational status"),
        sa.Column("setpoint", sa.Float(), nullable=True, comment="Temperature setpoint °C"),
        sa.PrimaryKeyConstraint("time", "device_id"),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
    )

    # =========================================================================
    # ENERGY METER TABLE (becomes hypertable in migration 002)
    # =========================================================================
    # Electrical energy consumption data for analytics and carbon tracking.
    # =========================================================================
    op.create_table(
        "energy_meter",
        sa.Column("time", sa.DateTime(), nullable=False, comment="Reading timestamp (UTC)"),
        sa.Column("meter_id", sa.String(100), nullable=False, comment="Energy meter ID"),
        sa.Column("building_id", sa.Uuid(), nullable=False, comment="Building FK"),
        sa.Column("kwh", sa.Float(), nullable=False, comment="Energy consumed (kWh)"),
        sa.Column("voltage", sa.Float(), nullable=True, comment="Instantaneous voltage (V)"),
        sa.Column("current", sa.Float(), nullable=True, comment="Instantaneous current (A)"),
        sa.PrimaryKeyConstraint("time", "meter_id"),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
    )


def downgrade() -> None:
    # Drop tables in reverse order to respect foreign key dependencies
    op.drop_table("energy_meter")
    op.drop_table("hvac_status")
    op.drop_table("sensor_readings")
    op.drop_table("recommendations")
    op.drop_table("forecasts")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("zones")
    op.drop_table("buildings")
    # Drop the enum type created for user roles
    sa.Enum(name="userrole").drop(op.get_bind())
