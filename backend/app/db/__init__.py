# =============================================================================
# db/__init__.py — Database Package
# =============================================================================
# PURPOSE: Marks the db/ directory as a Python package.
#
# This package contains:
#   - base.py    → SQLAlchemy DeclarativeBase (shared by all ORM models)
#   - engine.py  → Async database engine and session factory
#   - session.py → FastAPI dependency that provides DB sessions to routes
# =============================================================================
