import uuid
from datetime import datetime

from pydantic import BaseModel

from chat.models import MessageRole


class ChatRequest(BaseModel):
    agent_id: uuid.UUID
    message: str
    conversation_id: uuid.UUID | None = None


class TextDeltaEvent(BaseModel):
    type: str = "text_delta"
    content: str


class ToolCallStartEvent(BaseModel):
    type: str = "tool_call_start"
    name: str
    call_id: str


class ToolCallResultEvent(BaseModel):
    type: str = "tool_call_result"
    call_id: str
    result: str


class DoneEvent(BaseModel):
    type: str = "done"
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    usage: dict | None = None


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: MessageRole
    content: str
    tool_calls: dict | None
    token_usage: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: str
    agent_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime | None
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: str
    agent_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime | None
    messages: list[MessageResponse]

    model_config = {"from_attributes": True}
