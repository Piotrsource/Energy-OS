from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderRead(BaseModel):
    id: UUID
    offer_id: UUID
    request_id: UUID
    seller_id: UUID
    buyer_id: UUID
    matched_wh: int
    price_cents_per_kwh: int
    status: str
    matched_at: datetime
    settled_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
