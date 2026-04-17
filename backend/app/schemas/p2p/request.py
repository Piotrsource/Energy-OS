from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EnergyRequestCreate(BaseModel):
    quantity_wh: int = Field(..., gt=0, description="Energy to buy in Wh")
    max_price_cents_per_kwh: int = Field(..., gt=0, description="Max price willing to pay")
    preferred_from: datetime
    preferred_until: datetime


class EnergyRequestRead(BaseModel):
    id: UUID
    buyer_id: UUID
    quantity_wh: int
    max_price_cents_per_kwh: int
    preferred_from: datetime
    preferred_until: datetime
    remaining_wh: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
