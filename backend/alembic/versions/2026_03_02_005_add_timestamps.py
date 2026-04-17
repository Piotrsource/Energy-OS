"""Phase 1 — add created_at / updated_at to buildings, zones, users

Revision ID: 005_timestamps
Revises: 004_p2p_trading
Create Date: 2026-03-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_timestamps"
down_revision: Union[str, None] = "004_p2p_trading"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("buildings", "zones", "users"):
        op.add_column(
            table,
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )


def downgrade() -> None:
    for table in ("users", "zones", "buildings"):
        op.drop_column(table, "updated_at")
        op.drop_column(table, "created_at")
