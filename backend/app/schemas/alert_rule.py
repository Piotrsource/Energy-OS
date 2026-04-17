from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AlertRuleCreate(BaseModel):
    building_id: UUID
    zone_id: UUID | None = None
    sensor_type: str = Field(..., max_length=50)
    condition: str = Field(..., pattern="^(gt|lt|eq|gte|lte)$")
    threshold: float
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    enabled: bool = True
    name: str = Field(default="", max_length=255)


class AlertRuleUpdate(BaseModel):
    sensor_type: str | None = Field(None, max_length=50)
    condition: str | None = Field(None, pattern="^(gt|lt|eq|gte|lte)$")
    threshold: float | None = None
    severity: str | None = Field(None, pattern="^(low|medium|high|critical)$")
    enabled: bool | None = None
    name: str | None = Field(None, max_length=255)


class AlertRuleRead(BaseModel):
    id: UUID
    building_id: UUID
    zone_id: UUID | None
    sensor_type: str
    condition: str
    threshold: float
    severity: str
    enabled: bool
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
