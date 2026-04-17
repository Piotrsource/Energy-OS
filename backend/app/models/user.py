# =============================================================================
# models/user.py — User ORM Model
# =============================================================================
# PURPOSE: Represents a platform operator or administrator. Users authenticate
# via JWT tokens and have role-based access control (RBAC) that determines
# which API endpoints they can access.
#
# ROLES (defined as UserRole enum):
#   - admin:            Full access. Can create users, manage all buildings.
#   - facility_manager: Can manage buildings/zones they're assigned to,
#                       create forecasts and recommendations.
#   - technician:       Read-only access to data. Can submit sensor readings
#                       and approve/reject recommendations.
#
# SECURITY:
#   - Passwords are stored as bcrypt hashes (never plaintext).
#   - The password_hash column should NEVER appear in API responses.
#   - Email is unique and indexed for fast login lookups.
#
# TABLE: users
# COLUMNS: id (UUID PK), building_id (FK), name, email, role, password_hash
# RELATIONSHIPS: building (many-to-one)
# =============================================================================

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    """
    Enumeration of user roles for role-based access control.

    Inherits from str so that the enum values serialize cleanly to JSON
    (e.g., "admin" instead of "UserRole.ADMIN").
    """
    ADMIN = "admin"
    FACILITY_MANAGER = "facility_manager"
    TECHNICIAN = "technician"


class User(Base):
    """
    A platform user with authentication credentials and role-based permissions.
    """
    __tablename__ = "users"

    # -------------------------------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique user identifier (UUID v4)"
    )

    # -------------------------------------------------------------------------
    # FOREIGN KEY — Links user to their primary building
    # -------------------------------------------------------------------------
    building_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buildings.id"),
        nullable=False,
        comment="The building this user is primarily associated with"
    )

    # -------------------------------------------------------------------------
    # USER ATTRIBUTES
    # -------------------------------------------------------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Full name of the user"
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email address (used for login). Must be unique across all users."
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=UserRole.TECHNICIAN,
        comment="User role: admin, facility_manager, or technician"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt password hash. NEVER expose this in API responses."
    )

    # -------------------------------------------------------------------------
    # TIMESTAMPS (Phase 1)
    # -------------------------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # -------------------------------------------------------------------------
    # RELATIONSHIPS
    # -------------------------------------------------------------------------
    building = relationship("Building", back_populates="users")
