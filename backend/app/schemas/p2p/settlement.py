from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SettlementRead(BaseModel):
    id: UUID
    order_id: UUID
    interval_start: datetime
    interval_end: datetime
    contracted_wh: int
    actual_delivered_wh: int
    settlement_cents: int
    platform_fee_cents: int
    seller_credit_cents: int
    buyer_debit_cents: int
    shortfall_flag: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
