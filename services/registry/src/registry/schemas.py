import uuid
from datetime import datetime

from pydantic import BaseModel

from registry.models import AgentStatus


class AgentCreate(BaseModel):
    name: str
    version: str
    description: str | None = None
    owner: str
    endpoint_url: str | None = None
    auth_config: dict | None = None
    metadata: dict | None = None


class AgentUpdate(BaseModel):
    name: str | None = None
    version: str | None = None
    description: str | None = None
    owner: str | None = None
    endpoint_url: str | None = None
    status: AgentStatus | None = None
    auth_config: dict | None = None
    metadata: dict | None = None


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    status: AgentStatus
    description: str | None
    owner: str
    endpoint_url: str | None
    auth_config: dict | None
    metadata: dict | None
    last_heartbeat_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    created_by: str | None

    model_config = {"from_attributes": True}
