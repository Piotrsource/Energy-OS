# =============================================================================
# db/base.py — SQLAlchemy Declarative Base
# =============================================================================
# PURPOSE: Define the single DeclarativeBase class that ALL ORM models inherit
# from. This ensures every model shares one unified metadata object, which is
# critical for two reasons:
#
#   1. Alembic uses Base.metadata to detect all tables and generate migrations.
#      If a model inherits from a different base, Alembic won't see it.
#
#   2. SQLAlchemy resolves foreign key relationships through metadata.
#      All related models must share the same metadata to use relationship().
#
# USAGE:
#   from app.db.base import Base
#
#   class Building(Base):
#       __tablename__ = "buildings"
#       ...
# =============================================================================

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models in this application.

    All models MUST inherit from this class so they are registered
    in the shared metadata and discovered by Alembic migrations.
    """
    pass
