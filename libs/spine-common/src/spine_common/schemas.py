from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Service health status."""

    status: str = Field(description="Health status: 'ok' or 'degraded'")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(description="Human-readable error message")
    status_code: int = Field(description="HTTP status code")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list wrapper."""

    items: list[T] = Field(description="Page of results")
    total: int = Field(description="Total items matching query")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Items per page")
