import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from chat.models import MessageRole
from chat.orchestrator import AgentOrchestrator
from chat.schemas import (
    ChatRequest,
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
)
from chat.service import ConversationService
from spine_common.schemas import PaginatedResponse

router = APIRouter(prefix="/v1", tags=["chat"])


async def get_session() -> AsyncSession:  # type: ignore[misc]
    raise NotImplementedError("Overridden at app startup")


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ConversationService:
    return ConversationService(session)


def get_user_id(request: Request) -> str:
    return request.headers.get("x-user-id", "anonymous")


@router.post("/chat")
async def chat(
    data: ChatRequest,
    request: Request,
    service: Annotated[ConversationService, Depends(get_service)],
) -> EventSourceResponse:
    user_id = get_user_id(request)
    orchestrator: AgentOrchestrator = request.app.state.orchestrator

    agent_id = data.agent_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

    if data.conversation_id:
        conv = await service.get(data.conversation_id)
        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = await service.create(user_id=user_id, agent_id=agent_id, title=data.message[:100])

    await service.add_message(conv.id, MessageRole.USER, data.message)

    history = [{"role": m.role.value, "content": m.content} for m in (conv.messages or [])]

    async def event_generator():  # type: ignore[no-untyped-def]
        full_content = ""
        async for event in orchestrator.stream_response(agent_id, data.message, history):
            if event["type"] == "text_delta":
                full_content += event["content"]
            yield {"event": event["type"], "data": json.dumps(event)}

        await service.add_message(conv.id, MessageRole.ASSISTANT, full_content)

    return EventSourceResponse(event_generator())


@router.get("/conversations", response_model=PaginatedResponse[ConversationResponse])
async def list_conversations(
    request: Request,
    service: Annotated[ConversationService, Depends(get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ConversationResponse]:
    user_id = get_user_id(request)
    convs, total = await service.list_for_user(user_id, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[ConversationResponse.model_validate(c) for c in convs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    service: Annotated[ConversationService, Depends(get_service)],
) -> ConversationDetailResponse:
    conv = await service.get(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetailResponse(
        id=conv.id,
        user_id=conv.user_id,
        agent_id=conv.agent_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageResponse.model_validate(m) for m in conv.messages],
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    service: Annotated[ConversationService, Depends(get_service)],
) -> None:
    if not await service.delete(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
