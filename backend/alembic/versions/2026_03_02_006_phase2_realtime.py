"""Phase 2 — Real-Time Intelligence: alert_rules, alerts, notifications,
continuous aggregates, and retention policies.

Revision ID: 006_phase2_realtime
Revises: 005_timestamps
Create Date: 2026-03-02
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "006_phase2_realtime"
down_revision: Union[str, None] = "005_timestamps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── alert_rules ──────────────────────────────────────────────────────
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("building_id", sa.Uuid(), sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sensor_type", sa.String(50), nullable=False),
        sa.Column("condition", sa.String(10), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── alerts ───────────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("rule_id", sa.Uuid(), sa.ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("sensor_id", sa.String(100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_alerts_rule_id", "alerts", ["rule_id"])
    op.create_index("ix_alerts_triggered_at", "alerts", ["triggered_at"])

    # ── notifications ────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_id", sa.Uuid(), sa.ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", sa.String(20), nullable=False, server_default="in_app"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.String(1000), nullable=False, server_default=""),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    # ── Continuous aggregates (raw SQL — TimescaleDB-specific) ───────────
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 hour', time)  AS bucket,
            building_id,
            zone_id,
            sensor_type,
            AVG(value)   AS avg_value,
            MIN(value)   AS min_value,
            MAX(value)   AS max_value,
            COUNT(*)     AS sample_count
        FROM sensor_readings
        GROUP BY bucket, building_id, zone_id, sensor_type
        WITH NO DATA;
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_daily
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 day', time)  AS bucket,
            building_id,
            zone_id,
            sensor_type,
            AVG(value)   AS avg_value,
            MIN(value)   AS min_value,
            MAX(value)   AS max_value,
            COUNT(*)     AS sample_count
        FROM sensor_readings
        GROUP BY bucket, building_id, zone_id, sensor_type
        WITH NO DATA;
    """)

    # Refresh policies: materialize within 30 seconds of new data
    op.execute("""
        SELECT add_continuous_aggregate_policy('sensor_readings_hourly',
            start_offset    => INTERVAL '3 hours',
            end_offset      => INTERVAL '1 hour',
            schedule_interval => INTERVAL '30 seconds',
            if_not_exists   => TRUE);
    """)
    op.execute("""
        SELECT add_continuous_aggregate_policy('sensor_readings_daily',
            start_offset    => INTERVAL '3 days',
            end_offset      => INTERVAL '1 day',
            schedule_interval => INTERVAL '1 minute',
            if_not_exists   => TRUE);
    """)

    # ── Data retention policies ──────────────────────────────────────────
    op.execute("""
        SELECT add_retention_policy('sensor_readings',
            drop_after => INTERVAL '90 days',
            if_not_exists => TRUE);
    """)
    op.execute("""
        SELECT add_retention_policy('sensor_readings_hourly',
            drop_after => INTERVAL '1 year',
            if_not_exists => TRUE);
    """)


def downgrade() -> None:
    op.execute("SELECT remove_retention_policy('sensor_readings_hourly', if_exists => TRUE);")
    op.execute("SELECT remove_retention_policy('sensor_readings', if_exists => TRUE);")
    op.execute("SELECT remove_continuous_aggregate_policy('sensor_readings_daily', if_not_exists => TRUE);")
    op.execute("SELECT remove_continuous_aggregate_policy('sensor_readings_hourly', if_not_exists => TRUE);")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS sensor_readings_daily CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS sensor_readings_hourly CASCADE;")
    op.drop_table("notifications")
    op.drop_table("alerts")
    op.drop_table("alert_rules")
