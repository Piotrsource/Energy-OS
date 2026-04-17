from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TradingRuleCreate(BaseModel):
    rule_type: str = Field(..., pattern="^(auto_sell|auto_buy)$")
    conditions_json: dict = Field(..., description="Rule trigger conditions")
    action_json: dict = Field(..., description="Actions when rule fires")
    description: str | None = None
    enabled: bool = True


class TradingRuleUpdate(BaseModel):
    conditions_json: dict | None = None
    action_json: dict | None = None
    description: str | None = None
    enabled: bool | None = None


class TradingRuleRead(BaseModel):
    id: UUID
    user_id: UUID
    rule_type: str
    conditions_json: dict
    action_json: dict
    enabled: bool
    description: str | None
    last_triggered_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradingRuleTestResult(BaseModel):
    rule_id: UUID
    would_trigger: bool
    reason: str
    simulated_offer: dict | None = None
    simulated_request: dict | None = None
