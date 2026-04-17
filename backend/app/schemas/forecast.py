# =============================================================================
# schemas/forecast.py — Forecast Request/Response Schemas
# =============================================================================
# PURPOSE: Define Pydantic models for AI forecast CRUD operations.
#
# Forecasts are created by the AI/ML pipeline and consumed by the dashboard
# and the optimization engine. They predict future values (energy, occupancy,
# temperature) for specific zones at specific times.
#
# ENDPOINTS USING THESE SCHEMAS:
#   POST /api/v1/forecasts              → ForecastCreate (request body)
#   GET  /api/v1/forecasts?building_id= → list[ForecastRead] (response)
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ForecastCreate(BaseModel):
    """
    Request body for inserting a new AI forecast.
    Typically called by the ML pipeline after generating predictions.
    """
    zone_id: UUID = Field(..., description="The zone this forecast applies to")
    forecast_type: str = Field(
        ...,
        max_length=50,
        description="Prediction type: energy_consumption, occupancy, temperature, hvac_load"
    )
    predicted_value: float = Field(..., description="The predicted value (units depend on type)")
    forecast_time: datetime = Field(..., description="The future timestamp this prediction is for")


class ForecastRead(BaseModel):
    """
    Full forecast representation returned in API responses.
    """
    id: UUID = Field(..., description="Unique forecast identifier")
    zone_id: UUID = Field(..., description="Target zone ID")
    forecast_type: str = Field(..., description="Prediction type")
    predicted_value: float = Field(..., description="Predicted value")
    forecast_time: datetime = Field(..., description="Future time predicted")
    created_at: datetime = Field(..., description="When this forecast was generated")

    model_config = ConfigDict(from_attributes=True)
