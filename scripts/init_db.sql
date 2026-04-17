-- =============================================================================
-- init_db.sql — Database Initialization Script
-- =============================================================================
-- This script runs ONCE when the PostgreSQL container is created for the
-- first time. It is mounted into /docker-entrypoint-initdb.d/ by Docker.
--
-- Purpose:
--   Enable the TimescaleDB extension so that Alembic migrations can later
--   convert regular tables into hypertables for time-series data storage.
--
-- TimescaleDB provides:
--   - Automatic time-based partitioning (chunks) for sensor data
--   - Efficient time-range queries via chunk exclusion
--   - time_bucket() function for aggregation (used in analytics endpoints)
--   - Compression policies for long-term storage optimization
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
