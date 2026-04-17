"""Seed default admin user and demo building

Revision ID: 003_seed_admin
Revises: 002_hypertables
Create Date: 2026-03-02

PURPOSE:
    Insert a default admin user so the platform is usable immediately after
    setup. Also creates a demo building and zone so the admin has something
    to work with without needing to call the API first.

    DEFAULT CREDENTIALS:
        Email:    admin@energyplatform.local
        Password: admin123 (bcrypt-hashed below)
        Role:     admin

    WARNING: Change this password immediately in production!
    This seed data exists purely for development convenience.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.auth.passwords import hash_password

revision: str = "003_seed_admin"
down_revision: Union[str, None] = "002_hypertables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hash the default password at migration time using the same bcrypt
# library that the app uses for verification — guarantees compatibility.
ADMIN_PASSWORD_HASH = hash_password("admin123")

# Fixed UUIDs for seed data so they're predictable in development
DEMO_BUILDING_ID = "00000000-0000-4000-8000-000000000001"
DEMO_ZONE_ID = "00000000-0000-4000-8000-000000000002"
ADMIN_USER_ID = "00000000-0000-4000-8000-000000000003"


def upgrade() -> None:
    # =========================================================================
    # CREATE DEMO BUILDING
    # =========================================================================
    # A sample building so the admin user has an entity to associate with
    # and can immediately test API endpoints.
    # NOTE: We use sa.text().bindparams() because Alembic's op.execute()
    # only accepts a single argument — it does NOT support a separate
    # params dict like SQLAlchemy's connection.execute() does.
    # =========================================================================
    op.execute(
        sa.text(
            "INSERT INTO buildings (id, name, address, type, timezone) "
            "VALUES (:id, :name, :address, :type, :timezone) "
            "ON CONFLICT DO NOTHING"
        ).bindparams(
            id=DEMO_BUILDING_ID,
            name="Demo Hotel",
            address="123 Energy Street, Smart City, SC 10001",
            type="hotel",
            timezone="UTC",
        )
    )

    # =========================================================================
    # CREATE DEMO ZONE
    # =========================================================================
    # A sample zone within the demo building for testing forecasts,
    # recommendations, and sensor data endpoints.
    # =========================================================================
    op.execute(
        sa.text(
            "INSERT INTO zones (id, building_id, name, floor) "
            "VALUES (:id, :building_id, :name, :floor) "
            "ON CONFLICT DO NOTHING"
        ).bindparams(
            id=DEMO_ZONE_ID,
            building_id=DEMO_BUILDING_ID,
            name="Lobby",
            floor=1,
        )
    )

    # =========================================================================
    # CREATE ADMIN USER
    # =========================================================================
    # Default admin account for initial platform access.
    # Password "admin123" is stored as a bcrypt hash.
    # =========================================================================
    op.execute(
        sa.text(
            "INSERT INTO users (id, building_id, name, email, role, password_hash) "
            "VALUES (:id, :building_id, :name, :email, :role, :password_hash) "
            "ON CONFLICT DO NOTHING"
        ).bindparams(
            id=ADMIN_USER_ID,
            building_id=DEMO_BUILDING_ID,
            name="Platform Admin",
            email="admin@energyplatform.local",
            role="admin",
            password_hash=ADMIN_PASSWORD_HASH,
        )
    )


def downgrade() -> None:
    # Remove seed data in reverse order (respecting FK dependencies)
    # Same pattern: bind params directly to sa.text() via .bindparams()
    op.execute(sa.text("DELETE FROM users WHERE id = :id").bindparams(id=ADMIN_USER_ID))
    op.execute(sa.text("DELETE FROM zones WHERE id = :id").bindparams(id=DEMO_ZONE_ID))
    op.execute(sa.text("DELETE FROM buildings WHERE id = :id").bindparams(id=DEMO_BUILDING_ID))
