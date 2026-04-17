# =============================================================================
# db/engine.py — Async Database Engine and Session Factory
# =============================================================================
# PURPOSE: Create and configure the SQLAlchemy async engine and session factory.
# These are the core objects that manage database connections for the entire app.
#
# HOW IT WORKS:
#   - The engine manages a pool of database connections (default: 10 connections,
#     with overflow up to 20 for traffic spikes).
#   - The session factory (AsyncSessionLocal) creates individual sessions that
#     are used by FastAPI route handlers to execute queries.
#   - The engine is created once at module import time and disposed during
#     the FastAPI shutdown lifecycle event (see main.py).
#
# CONNECTION FLOW:
#   FastAPI request → get_db() dependency → AsyncSessionLocal() → engine pool
#
# USAGE:
#   from app.db.engine import engine, AsyncSessionLocal
# =============================================================================

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings


# =============================================================================
# ASYNC ENGINE
# =============================================================================
# Creates a connection pool to the PostgreSQL/TimescaleDB database.
# - echo=True (when debug=True): Logs every SQL statement to stdout, useful
#   for development debugging but should be False in production.
# - pool_size=10: Maintains 10 persistent connections in the pool.
# - max_overflow=20: Allows up to 20 additional connections during traffic spikes.
#   These overflow connections are closed after use, returning the pool to 10.
# =============================================================================
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
)

# =============================================================================
# SESSION FACTORY
# =============================================================================
# Configured to create AsyncSession instances bound to the engine above.
# - expire_on_commit=False: Prevents SQLAlchemy from marking objects as
#   "expired" after commit. Without this, accessing object attributes after
#   commit would trigger a lazy-load SQL query (which fails in async mode).
# =============================================================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
