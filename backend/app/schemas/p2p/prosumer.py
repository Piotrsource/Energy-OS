from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProsumerCreate(BaseModel):
    address: str = Field(..., description="Full street address")
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    solar_capacity_kw: float = Field(0.0, ge=0)
    battery_capacity_kwh: float = Field(0.0, ge=0)
    inverter_type: str | None = Field(None, max_length=100)
    meter_id: str = Field(..., max_length=200, description="Smart meter hardware ID")
    meter_provider: str | None = Field(None, max_length=100)
    accept_grid_agreement: bool = Field(False, description="Must accept before activation")


class ProsumerRead(BaseModel):
    id: UUID
    user_id: UUID
    address: str
    lat: float
    lng: float
    solar_capacity_kw: float
    battery_capacity_kwh: float
    inverter_type: str | None
    meter_id: str
    meter_provider: str | None
    grid_agreement_accepted_at: datetime | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProsumerUpdate(BaseModel):
    solar_capacity_kw: float | None = Field(None, ge=0)
    battery_capacity_kwh: float | None = Field(None, ge=0)
    inverter_type: str | None = None
    meter_id: str | None = Field(None, max_length=200)
    meter_provider: str | None = None


class MeterReadingCreate(BaseModel):
    time: datetime
    meter_id: str = Field(..., max_length=200)
    production_wh: int = Field(0, ge=0)
    consumption_wh: int = Field(0, ge=0)
    net_export_wh: int = Field(0)
    source: str = Field("api", max_length=50)


class MeterReadingRead(BaseModel):
    time: datetime
    meter_id: str
    production_wh: int
    consumption_wh: int
    net_export_wh: int
    source: str

    model_config = ConfigDict(from_attributes=True)
