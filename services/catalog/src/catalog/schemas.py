import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CapabilityCreate(BaseModel):
    """Register a new capability."""

    agent_id: uuid.UUID | None = Field(default=None, description="Agent that provides this capability")
    name: str = Field(description="Capability name")
    description: str | None = Field(default=None, description="What this capability does")
    input_schema: dict[str, Any] | None = Field(default=None, description="JSON Schema for input")
    output_schema: dict[str, Any] | None = Field(default=None, description="JSON Schema for output")
    tags: list[str] = Field(default=[], description="Tags for filtering and discovery")


class CapabilityUpdate(BaseModel):
    """Partial update — only provided fields are modified."""

    name: str | None = None
    description: str | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    tags: list[str] | None = None


class CapabilityResponse(BaseModel):
    """Capability record as returned by the API."""

    id: uuid.UUID
    agent_id: uuid.UUID | None
    name: str
    description: str | None
    input_schema: dict[str, Any] | None
    output_schema: dict[str, Any] | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ToolCreate(BaseModel):
    """Register a new tool."""

    name: str = Field(description="Tool name")
    description: str | None = Field(default=None, description="What this tool does")
    provider: str | None = Field(default=None, description="Tool provider (e.g. 'openai', 'custom')")
    input_schema: dict[str, Any] | None = Field(default=None, description="JSON Schema for input")
    output_schema: dict[str, Any] | None = Field(default=None, description="JSON Schema for output")
    tags: list[str] = Field(default=[], description="Tags for filtering and discovery")


class ToolUpdate(BaseModel):
    """Partial update — only provided fields are modified."""

    name: str | None = None
    description: str | None = None
    provider: str | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    tags: list[str] | None = None


class ToolResponse(BaseModel):
    """Tool record as returned by the API."""

    id: uuid.UUID
    name: str
    description: str | None
    provider: str | None
    input_schema: dict[str, Any] | None
    output_schema: dict[str, Any] | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
