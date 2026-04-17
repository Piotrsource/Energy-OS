from datetime import datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class NotificationRead(BaseModel):
    id: UUID
    user_id: UUID
    alert_id: UUID | None
    channel: str
    title: str
    body: str
    sent_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# ── Notification Preferences ──────────────────────────────────────────────


class NotificationPreferenceRead(BaseModel):
    id: UUID
    user_id: UUID
    in_app_enabled: bool
    email_enabled: bool
    min_severity: Literal["low", "medium", "high", "critical"]
    email_address: str | None
    quiet_start_hour: int | None
    quiet_end_hour: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    min_severity: Literal["low", "medium", "high", "critical"] | None = None
    email_address: str | None = None
    quiet_start_hour: int | None = Field(default=None, ge=0, le=23)
    quiet_end_hour: int | None = Field(default=None, ge=0, le=23)
