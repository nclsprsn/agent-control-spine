import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from registry.models import AgentStatus


class AgentCreate(BaseModel):
    """Register a new agent."""

    name: str = Field(description="Unique agent name")
    version: str = Field(description="Semantic version (e.g. 1.0.0)")
    description: str | None = Field(default=None, description="Human-readable description")
    owner: str = Field(description="Team or user owning this agent")
    endpoint_url: str | None = Field(default=None, description="Agent's HTTP endpoint URL")
    auth_config: dict[str, Any] | None = Field(default=None, description="Authentication configuration")
    metadata: dict[str, Any] | None = Field(default=None, description="Arbitrary key-value metadata")


class AgentUpdate(BaseModel):
    """Partial update — only provided fields are modified."""

    name: str | None = None
    version: str | None = None
    description: str | None = None
    owner: str | None = None
    endpoint_url: str | None = None
    status: AgentStatus | None = Field(default=None, description="Manually override agent status")
    auth_config: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    """Agent record as returned by the API."""

    id: uuid.UUID
    name: str
    version: str
    status: AgentStatus
    description: str | None
    owner: str
    endpoint_url: str | None
    auth_config: dict[str, Any] | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_")
    last_heartbeat_at: datetime | None = Field(description="Timestamp of last heartbeat")
    created_at: datetime
    updated_at: datetime | None
    created_by: str | None

    model_config = {"from_attributes": True}
