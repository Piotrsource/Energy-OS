# =============================================================================
# schemas/user.py — User Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for user management endpoints.
#
# SECURITY: The UserRead schema intentionally EXCLUDES password_hash.
# Passwords are only accepted as input (UserCreate) and never returned.
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST  /api/v1/users         → UserCreate (request body)
#   GET   /api/v1/users         → list[UserRead] (response)
#   PATCH /api/v1/users/{id}    → UserUpdate (request body)
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """
    Request body for creating a new user (POST /api/v1/users).
    Only admins can create users. The password is hashed before storage.
    """
    building_id: UUID = Field(..., description="Building the user is associated with")
    name: str = Field(..., max_length=255, description="User's full name")
    email: str = Field(..., max_length=255, description="Email address (must be unique)")
    role: str = Field(
        default="technician",
        description="User role: admin, facility_manager, or technician"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Plaintext password (will be bcrypt-hashed before storage)"
    )


class UserUpdate(BaseModel):
    """
    Request body for partial user updates (PATCH /api/v1/users/{id}).
    All fields are optional. Password changes re-hash the new password.
    """
    name: str | None = Field(None, max_length=255, description="New name")
    email: str | None = Field(None, max_length=255, description="New email")
    role: str | None = Field(None, description="New role")
    password: str | None = Field(None, min_length=8, description="New password")


class UserRead(BaseModel):
    id: UUID = Field(..., description="Unique user identifier")
    building_id: UUID = Field(..., description="Associated building ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
