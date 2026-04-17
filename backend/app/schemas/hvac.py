# =============================================================================
# schemas/hvac.py — HVAC Status Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for HVAC status ingestion and retrieval.
#
# HVAC DATA FLOW:
#   BMS/HVAC controllers → POST /api/v1/hvac/status (bulk insert)
#   Dashboard/API users  → GET  /api/v1/hvac/status  (query with filters)
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST /api/v1/hvac/status                                       → HvacStatusCreate (list)
#   GET  /api/v1/hvac/status?building_id=&zone_id=&start=&end=    → list[HvacStatusRead]
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HvacStatusCreate(BaseModel):
    """
    A single HVAC status snapshot to be inserted into the time-series database.
    The POST endpoint accepts a list of these for bulk ingestion.
    """
    time: datetime = Field(..., description="Timestamp of the status snapshot (UTC)")
    device_id: str = Field(..., max_length=100, description="Unique HVAC device hardware identifier")
    building_id: UUID = Field(..., description="Building where the HVAC device is installed")
    zone_id: UUID = Field(..., description="Zone the HVAC device serves")
    device_type: str = Field(
        ...,
        max_length=50,
        description="HVAC equipment type: ahu, chiller, boiler, fcu, vav"
    )
    status: str = Field(
        ...,
        max_length=50,
        description="Operational status: running, idle, off, fault, maintenance"
    )
    setpoint: float | None = Field(
        None,
        description="Temperature setpoint in °C (null if device has no setpoint)"
    )


class HvacStatusRead(BaseModel):
    """
    An HVAC status snapshot returned in query results.
    Matches the database row structure.
    """
    time: datetime = Field(..., description="Timestamp of the status snapshot")
    device_id: str = Field(..., description="HVAC device identifier")
    building_id: UUID = Field(..., description="Building ID")
    zone_id: UUID = Field(..., description="Zone ID")
    device_type: str = Field(..., description="Equipment type")
    status: str = Field(..., description="Operational status")
    setpoint: float | None = Field(None, description="Temperature setpoint in °C")

    model_config = ConfigDict(from_attributes=True)
