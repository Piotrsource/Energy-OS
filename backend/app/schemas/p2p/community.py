from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommunityCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    location_lat: float = Field(..., ge=-90, le=90)
    location_lng: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(5.0, gt=0, le=100)
    fee_discount_pct: int = Field(50, ge=0, le=100)


class CommunityRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    location_lat: float
    location_lng: float
    radius_km: float
    fee_discount_pct: int
    created_by: UUID
    created_at: datetime
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CommunityMemberRead(BaseModel):
    community_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunityDashboard(BaseModel):
    community_id: UUID
    community_name: str
    member_count: int
    total_trades: int
    total_kwh_traded: float
    total_value_cents: int
    avg_price_cents_per_kwh: float
    grid_independence_pct: float
    co2_avoided_kg: float
