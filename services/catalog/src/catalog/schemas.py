import uuid
from datetime import datetime

from pydantic import BaseModel


class CapabilityCreate(BaseModel):
    agent_id: uuid.UUID | None = None
    name: str
    description: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    tags: list[str] = []


class CapabilityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    tags: list[str] | None = None


class CapabilityResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID | None
    name: str
    description: str | None
    input_schema: dict | None
    output_schema: dict | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ToolCreate(BaseModel):
    name: str
    description: str | None = None
    provider: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    tags: list[str] = []


class ToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    provider: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    tags: list[str] | None = None


class ToolResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    provider: str | None
    input_schema: dict | None
    output_schema: dict | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
