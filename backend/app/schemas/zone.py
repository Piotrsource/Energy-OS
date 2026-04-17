# =============================================================================
# schemas/zone.py — Zone Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for zone CRUD operations.
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST /api/v1/zones              → ZoneCreate (request body)
#   GET  /api/v1/zones?building_id= → list[ZoneRead] (response)
#   GET  /api/v1/zones/{id}         → ZoneRead (response)
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ZoneCreate(BaseModel):
    """
    Request body for creating a new zone within a building.
    The building_id links the zone to its parent building.
    """
    building_id: UUID = Field(..., description="The building this zone belongs to")
    name: str = Field(..., max_length=255, description="Zone name, e.g. 'Floor 3 East Wing'")
    floor: int | None = Field(None, description="Floor number (optional)")


class ZoneRead(BaseModel):
    id: UUID = Field(..., description="Unique zone identifier")
    building_id: UUID = Field(..., description="Parent building ID")
    name: str = Field(..., description="Zone name")
    floor: int | None = Field(None, description="Floor number")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
