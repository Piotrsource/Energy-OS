# =============================================================================
# schemas/sensor.py — Sensor Reading Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for sensor data ingestion and retrieval.
#
# SENSOR DATA FLOW:
#   IoT sensors/gateways → POST /api/v1/sensors/readings (bulk insert)
#   Dashboard/API users  → GET  /api/v1/sensors/readings (query with filters)
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST /api/v1/sensors/readings                                 → SensorReadingCreate (list)
#   GET  /api/v1/sensors/readings?building_id=&zone_id=&start=&end= → list[SensorReadingRead]
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

SENSOR_VALUE_RANGES: dict[str, tuple[float, float]] = {
    "temperature": (-50.0, 80.0),
    "humidity": (0.0, 100.0),
    "co2": (0.0, 10_000.0),
    "occupancy": (0.0, 10_000.0),
    "light_level": (0.0, 200_000.0),
    "power": (0.0, 1_000_000.0),
}


class SensorReadingCreate(BaseModel):
    time: datetime = Field(..., description="Timestamp of the reading (UTC)")
    sensor_id: str = Field(..., max_length=100, description="Unique sensor hardware identifier")
    building_id: UUID = Field(..., description="Building where the sensor is installed")
    zone_id: UUID = Field(..., description="Zone where the sensor operates")
    sensor_type: str = Field(
        ...,
        max_length=50,
        description="What the sensor measures: temperature, humidity, co2, occupancy, light_level, power"
    )
    value: float = Field(..., description="Measured value (units depend on sensor_type)")

    @model_validator(mode="after")
    def validate_value_range(self):
        bounds = SENSOR_VALUE_RANGES.get(self.sensor_type)
        if bounds:
            lo, hi = bounds
            if not (lo <= self.value <= hi):
                raise ValueError(
                    f"Sensor value {self.value} out of range for type "
                    f"'{self.sensor_type}' (expected {lo}–{hi})"
                )
        return self


class SensorReadingRead(BaseModel):
    """
    A sensor reading returned in query results.
    Matches the database row structure.
    """
    time: datetime = Field(..., description="Timestamp of the reading")
    sensor_id: str = Field(..., description="Sensor hardware identifier")
    building_id: UUID = Field(..., description="Building ID")
    zone_id: UUID = Field(..., description="Zone ID")
    sensor_type: str = Field(..., description="Measurement type")
    value: float = Field(..., description="Measured value")

    model_config = ConfigDict(from_attributes=True)
