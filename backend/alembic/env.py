# =============================================================================
# alembic/env.py — Alembic Migration Environment
# =============================================================================
# PURPOSE: Configure how Alembic connects to the database and generates
# migrations. This is the most complex single file in the migration system
# because it must handle several special cases:
#
#   1. SYNC CONNECTION: Alembic's autogenerate requires a synchronous database
#      connection (psycopg2), even though the app uses async (asyncpg).
#
#   2. TIMESCALEDB FILTERING: TimescaleDB creates internal schemas and indexes
#      that Alembic would try to drop on every autogenerate run. We filter
#      these out to prevent false migration diffs.
#
#   3. MODEL DISCOVERY: All ORM models must be imported before autogenerate
#      runs so their tables appear in Base.metadata.
#
# USAGE:
#   alembic revision --autogenerate -m "description"  → generate migration
#   alembic upgrade head                              → apply all migrations
#   alembic downgrade -1                              → roll back one migration
#   alembic history                                   → show migration history
# =============================================================================

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy import engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# PYTHON PATH SETUP
# ---------------------------------------------------------------------------
# Ensure the backend root directory (/app in Docker) is on the Python path
# so that `from app.config import settings` resolves correctly.
# Without this, Alembic can't find the app package.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ---------------------------------------------------------------------------
# IMPORT APPLICATION CONFIG AND MODELS
# ---------------------------------------------------------------------------
# We must import settings to get the database URL, and import all models
# so their tables are registered in Base.metadata for autogenerate.
# ---------------------------------------------------------------------------
from app.config import settings
from app.db.base import Base

# This import triggers all model files to register with Base.metadata.
# Without it, Alembic would see zero tables and generate empty migrations.
from app.models import *  # noqa: F401, F403

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the placeholder sqlalchemy.url with the real sync database URL
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Target metadata — Alembic compares this against the live database
target_metadata = Base.metadata


# =============================================================================
# TIMESCALEDB FILTERING
# =============================================================================
# TimescaleDB creates internal schemas and auto-managed indexes that should
# NOT appear in Alembic migrations. Without these filters, every autogenerate
# would produce DROP INDEX statements for TimescaleDB-internal objects.
# =============================================================================

# TimescaleDB internal schemas to ignore during migration generation
TIMESCALE_INTERNAL_SCHEMAS = {
    "_timescaledb_catalog",
    "_timescaledb_internal",
    "_timescaledb_config",
    "_timescaledb_cache",
    "timescaledb_information",
    "timescaledb_experimental",
}

# Tables that are converted to hypertables (TimescaleDB manages their indexes)
HYPERTABLE_TABLES = {"sensor_readings", "hvac_status", "energy_meter"}


def include_name(name, type_, parent_names):
    """
    Filter callback: exclude TimescaleDB internal schemas from reflection.

    Called during database schema reflection. Returning False for a schema
    name prevents Alembic from inspecting any objects in that schema.
    """
    if type_ == "schema" and name in TIMESCALE_INTERNAL_SCHEMAS:
        return False
    return True


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter callback: exclude TimescaleDB auto-generated indexes.

    TimescaleDB creates indexes on hypertable chunks automatically.
    These indexes don't exist in our SQLAlchemy models, so Alembic
    would generate DROP INDEX statements for them on every autogenerate.
    This filter prevents that by skipping indexes on hypertable tables
    that aren't explicitly defined in our models.
    """
    if type_ == "index" and hasattr(object, "table"):
        table_name = object.table.name if hasattr(object.table, "name") else ""
        if table_name in HYPERTABLE_TABLES:
            # Only keep indexes that are explicitly defined in our models
            model_table = target_metadata.tables.get(table_name)
            if model_table is not None:
                model_index_names = {idx.name for idx in model_table.indexes}
                if name not in model_index_names:
                    return False
    return True


# =============================================================================
# MIGRATION RUNNERS
# =============================================================================

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generates SQL scripts without
    connecting to the database. Useful for review or manual application.

    Usage: alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — connects to the database and
    applies migrations directly. This is the normal mode of operation.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool connections for migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run based on how Alembic was invoked
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
