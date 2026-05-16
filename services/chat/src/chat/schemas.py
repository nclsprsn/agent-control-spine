import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chat.models import MessageRole


class ChatRequest(BaseModel):
    """Send a chat message."""

    agent_id: uuid.UUID | None = Field(default=None, description="Target agent ID (null for default)")
    message: str = Field(description="User message content")
    conversation_id: uuid.UUID | None = Field(default=None, description="Continue existing conversation")


class TextDeltaEvent(BaseModel):
    """SSE event: incremental text content."""

    type: str = "text_delta"
    content: str


class ToolCallStartEvent(BaseModel):
    """SSE event: tool invocation started."""

    type: str = "tool_call_start"
    name: str
    call_id: str


class ToolCallResultEvent(BaseModel):
    """SSE event: tool invocation completed."""

    type: str = "tool_call_result"
    call_id: str
    result: str


class DoneEvent(BaseModel):
    """SSE event: stream complete."""

    type: str = "done"
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    usage: dict[str, Any] | None = None


class MessageResponse(BaseModel):
    """Single message in a conversation."""

    id: uuid.UUID
    role: MessageRole
    content: str
    tool_calls: dict[str, Any] | None
    token_usage: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Conversation summary (without messages)."""

    id: uuid.UUID
    user_id: str
    agent_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime | None
    message_count: int = Field(default=0, description="Total messages in conversation")

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    """Conversation with full message history."""

    id: uuid.UUID
    user_id: str
    agent_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime | None
    messages: list[MessageResponse]

    model_config = {"from_attributes": True}
