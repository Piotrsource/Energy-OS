# =============================================================================
# schemas/building.py — Building Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for building CRUD operations.
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST   /api/v1/buildings          → BuildingCreate (request body)
#   GET    /api/v1/buildings           → list[BuildingRead] (response)
#   GET    /api/v1/buildings/{id}      → BuildingRead (response)
#   PATCH  /api/v1/buildings/{id}      → BuildingUpdate (request body)
#   DELETE /api/v1/buildings/{id}      → MessageResponse (response)
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BuildingBase(BaseModel):
    """
    Shared fields between create and read schemas.
    DRY: avoids repeating field definitions in both schemas.
    """
    name: str = Field(..., max_length=255, description="Human-readable building name")
    address: str = Field(..., description="Full street address")
    type: str = Field(..., max_length=100, description="Building type: hotel, office, retail, etc.")
    timezone: str = Field(default="UTC", max_length=50, description="IANA timezone, e.g. 'America/New_York'")


class BuildingCreate(BuildingBase):
    """
    Request body for creating a new building (POST /api/v1/buildings).
    All fields from BuildingBase are required.
    """
    pass


class BuildingUpdate(BaseModel):
    """
    Request body for partial building updates (PATCH /api/v1/buildings/{id}).
    All fields are optional — only provided fields are updated.
    """
    name: str | None = Field(None, max_length=255, description="New building name")
    address: str | None = Field(None, description="New address")
    type: str | None = Field(None, max_length=100, description="New building type")
    timezone: str | None = Field(None, max_length=50, description="New timezone")


class BuildingRead(BuildingBase):
    id: UUID = Field(..., description="Unique building identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
