from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WalletRead(BaseModel):
    id: UUID
    user_id: UUID
    energy_credits_wh: int
    cash_balance_cents: int
    currency: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletDeposit(BaseModel):
    amount_cents: int = Field(..., gt=0, description="Amount to deposit in cents")


class WalletWithdraw(BaseModel):
    amount_cents: int = Field(..., gt=0, description="Amount to withdraw in cents")


class LedgerEntryRead(BaseModel):
    id: UUID
    wallet_id: UUID
    entry_type: str
    amount_cents: int
    energy_wh: int
    counterparty_wallet_id: UUID | None
    order_id: UUID | None
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
