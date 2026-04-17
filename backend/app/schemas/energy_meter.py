# =============================================================================
# schemas/energy_meter.py — Energy Meter Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for energy meter data ingestion and retrieval.
#
# NOTE: The analytics response schemas (EnergySummary, CarbonEmissions) live in
# schemas/energy.py. This file is specifically for raw meter data CRUD.
#
# ENERGY METER DATA FLOW:
#   Smart meters/gateways → POST /api/v1/energy-meters/readings (bulk insert)
#   Dashboard/API users   → GET  /api/v1/energy-meters/readings  (query with filters)
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST /api/v1/energy-meters/readings                           → EnergyMeterCreate (list)
#   GET  /api/v1/energy-meters/readings?building_id=&start=&end= → list[EnergyMeterRead]
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EnergyMeterCreate(BaseModel):
    """
    A single energy meter reading to be inserted into the time-series database.
    The POST endpoint accepts a list of these for bulk ingestion.
    """
    time: datetime = Field(..., description="Timestamp of the meter reading (UTC)")
    meter_id: str = Field(..., max_length=100, description="Unique energy meter identifier")
    building_id: UUID = Field(..., description="Building where the meter is installed")
    kwh: float = Field(..., description="Energy consumed in kilowatt-hours since last reading")
    voltage: float | None = Field(None, description="Instantaneous voltage in volts")
    current: float | None = Field(None, description="Instantaneous current in amperes")


class EnergyMeterRead(BaseModel):
    """
    An energy meter reading returned in query results.
    Matches the database row structure.
    """
    time: datetime = Field(..., description="Timestamp of the meter reading")
    meter_id: str = Field(..., description="Meter identifier")
    building_id: UUID = Field(..., description="Building ID")
    kwh: float = Field(..., description="Energy consumed (kWh)")
    voltage: float | None = Field(None, description="Voltage (V)")
    current: float | None = Field(None, description="Current (A)")

    model_config = ConfigDict(from_attributes=True)
