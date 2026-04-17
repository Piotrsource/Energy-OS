from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AlertRead(BaseModel):
    id: UUID
    rule_id: UUID
    triggered_at: datetime
    sensor_id: str
    value: float
    acknowledged_at: datetime | None
    acknowledged_by: UUID | None

    model_config = ConfigDict(from_attributes=True)


class AlertAcknowledge(BaseModel):
    pass
