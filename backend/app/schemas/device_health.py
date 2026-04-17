from datetime import datetime
from pydantic import BaseModel


class DeviceHealthRead(BaseModel):
    sensor_id: str
    building_id: str
    zone_id: str
    sensor_type: str
    last_seen: datetime
    last_value: float
    status: str  # "online", "stale", "offline"
