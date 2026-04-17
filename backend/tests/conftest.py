"""
Shared test fixtures for the backend test suite.

Uses testcontainers with TimescaleDB for realistic PostgreSQL testing.
The container starts once per session; tables are truncated between tests
for isolation.

Architecture:
  - db_url (session): starts TimescaleDB container, creates schema
  - db_session (function): engine + session for test data setup (admin_user, etc.)
  - client (function): separate engine for HTTP handlers + patches app engine
    so health-check, middleware, and all endpoints use the test database
"""

import os
import uuid
from typing import AsyncGenerator

# Raise rate limit for tests to avoid 429s
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "10000")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.building import Building
from app.models.zone import Zone
from app.models.forecast import Forecast
from app.models.recommendation import Recommendation
from app.models.sensor_reading import SensorReading
from app.models.hvac_status import HvacStatus
from app.models.energy_meter import EnergyMeter
from app.auth.passwords import hash_password
from app.auth.jwt import create_access_token


# ---------------------------------------------------------------------------
# TimescaleDB container + schema — one per test session
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def db_url():
    """
    Start a TimescaleDB container and set up the schema.

    Returns the async database URL for the test container.
    The container is kept alive for the entire test session and torn down
    automatically at the end.
    """
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer(
        image="timescale/timescaledb:latest-pg16",
        username="test",
        password="test",
        dbname="test_db",
    ) as pg:
        host = pg.get_container_host_ip()
        port = pg.get_exposed_port(5432)
        sync_url = f"postgresql://test:test@{host}:{port}/test_db"
        async_url = f"postgresql+asyncpg://test:test@{host}:{port}/test_db"

        # ── Schema setup (synchronous, runs once) ────────────────────
        sync_engine = create_engine(sync_url)

        # Enable TimescaleDB extension
        with sync_engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE"))

        # Create all ORM tables
        Base.metadata.create_all(sync_engine)

        # Convert time-series tables to hypertables
        with sync_engine.begin() as conn:
            for table in ("sensor_readings", "hvac_status", "energy_meter"):
                conn.execute(text(
                    f"SELECT create_hypertable('{table}', 'time', "
                    f"if_not_exists => TRUE, migrate_data => TRUE)"
                ))

        sync_engine.dispose()

        yield async_url


# ---------------------------------------------------------------------------
# SQL for table truncation between tests
# ---------------------------------------------------------------------------
TRUNCATE_SQL = text(
    "TRUNCATE TABLE sensor_readings, hvac_status, energy_meter, "
    "forecasts, recommendations, zones, users, buildings CASCADE"
)


# ---------------------------------------------------------------------------
# Per-test database session for test data setup (admin_user, etc.)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session(db_url) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh engine + session per test.

    Tables are truncated before each test for isolation. This session is
    used for inserting test fixtures (buildings, users). A SEPARATE engine
    is created for the HTTP client so that Starlette middleware tasks
    don't share connections across task boundaries.
    """
    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)

    # Truncate all tables for clean state
    async with engine.begin() as conn:
        await conn.execute(TRUNCATE_SQL)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


# ---------------------------------------------------------------------------
# HTTP test client — patches app's DB engine and get_db dependency
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client(db_url, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP test client that:
    1. Creates its own engine + session factory for the test container
    2. Patches the app's engine module so health-check / middleware use test DB
    3. Overrides the get_db dependency to create fresh per-request sessions

    Using a separate engine from db_session avoids asyncpg's
    "Future attached to a different loop" error caused by Starlette's
    BaseHTTPMiddleware spawning sub-tasks.
    """
    import app.db.engine as engine_module

    # Create a separate engine for the HTTP request handlers
    handler_engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    handler_factory = async_sessionmaker(handler_engine, expire_on_commit=False)

    # Save originals
    orig_engine = engine_module.engine
    orig_factory = engine_module.AsyncSessionLocal

    # Patch the app's engine module so health-check and any code that
    # uses AsyncSessionLocal directly will hit the test database
    engine_module.engine = handler_engine
    engine_module.AsyncSessionLocal = handler_factory

    # Override FastAPI's get_db to create fresh sessions per request
    async def override_get_db():
        async with handler_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        yield ac

    # Restore originals
    app.dependency_overrides.clear()
    engine_module.engine = orig_engine
    engine_module.AsyncSessionLocal = orig_factory
    await handler_engine.dispose()


# ---------------------------------------------------------------------------
# Admin user + building
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user with a test building."""
    building_id = uuid.uuid4()

    building = Building(
        id=building_id,
        name="Test Building",
        address="123 Test St",
        type="hotel",
        timezone="UTC",
    )
    db_session.add(building)

    user = User(
        id=uuid.uuid4(),
        building_id=building_id,
        name="Test Admin",
        email="admin@test.local",
        role=UserRole.ADMIN,
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    """Generate a valid JWT token for the admin user."""
    return create_access_token(admin_user.id, admin_user.role.value)


@pytest_asyncio.fixture
async def auth_headers(admin_token: str) -> dict:
    """Authorization headers with a valid admin Bearer token."""
    return {"Authorization": f"Bearer {admin_token}"}


# ---------------------------------------------------------------------------
# Technician user (same building as admin, lower permissions)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def technician_user(db_session: AsyncSession, admin_user: User) -> User:
    """Create a technician-role user (same building as admin)."""
    user = User(
        id=uuid.uuid4(),
        building_id=admin_user.building_id,
        name="Test Technician",
        email="tech@test.local",
        role=UserRole.TECHNICIAN,
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def technician_token(technician_user: User) -> str:
    """Generate a valid JWT token for the technician user."""
    return create_access_token(technician_user.id, technician_user.role.value)


@pytest_asyncio.fixture
async def technician_headers(technician_token: str) -> dict:
    """Authorization headers with a technician Bearer token."""
    return {"Authorization": f"Bearer {technician_token}"}


# ---------------------------------------------------------------------------
# Convenience: test zone (requires admin_user for building FK)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_zone(db_session: AsyncSession, admin_user: User) -> Zone:
    """Create a zone in the test building."""
    zone = Zone(
        id=uuid.uuid4(),
        building_id=admin_user.building_id,
        name="Test Zone",
        floor=1,
    )
    db_session.add(zone)
    await db_session.commit()
    return zone
