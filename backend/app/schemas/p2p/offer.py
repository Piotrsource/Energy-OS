from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OfferCreate(BaseModel):
    quantity_wh: int = Field(..., gt=0, description="Energy to sell in Wh")
    price_cents_per_kwh: int = Field(..., gt=0, description="Ask price in cents per kWh")
    available_from: datetime
    available_until: datetime
    min_purchase_wh: int = Field(0, ge=0)
    auto_renew: bool = False


class OfferRead(BaseModel):
    id: UUID
    seller_id: UUID
    quantity_wh: int
    price_cents_per_kwh: int
    available_from: datetime
    available_until: datetime
    min_purchase_wh: int
    remaining_wh: int
    auto_renew: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
