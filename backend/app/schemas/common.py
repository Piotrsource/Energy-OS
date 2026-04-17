from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Human-readable error description")
    code: str = Field(..., description="Machine-readable error code")
    request_id: str = Field(default="", description="Request correlation ID")


class MessageResponse(BaseModel):
    message: str = Field(..., description="Status or success message")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)  # type: ignore[assignment]
    total_count: int = Field(..., description="Total items matching the query")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Page size used")

