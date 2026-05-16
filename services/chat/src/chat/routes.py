import json
import uuid
from base64 import urlsafe_b64decode
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from spine_common.schemas import PaginatedResponse
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

router = APIRouter(prefix="/v1", tags=["chat"])


async def get_session() -> AsyncSession:
    raise NotImplementedError("Overridden at app startup")


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ConversationService:
    return ConversationService(session)


def get_user_id(request: Request) -> str:
    if user_id := request.headers.get("x-user-id"):
        return user_id
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            payload = auth_header[7:].split(".")[1]
            padding = "=" * (4 - len(payload) % 4)
            claims = json.loads(urlsafe_b64decode(payload + padding))
            return claims.get("sub") or claims.get("preferred_username") or "anonymous"
        except IndexError, ValueError, json.JSONDecodeError:
            pass
    return "anonymous"


@router.post(
    "/chat",
    summary="Stream chat",
    description=(
        "Send a message and receive streaming SSE response. "
        "Creates or continues a conversation. "
        "Events: thinking_delta, text_delta, tool_call_start, tool_call_result, done."
    ),
)
async def chat(
    data: ChatRequest,
    request: Request,
    service: Annotated[ConversationService, Depends(get_service)],
) -> EventSourceResponse:
    user_id = get_user_id(request)
    orchestrator: AgentOrchestrator = request.app.state.orchestrator
    session_factory = request.app.state.session_factory

    agent_id = data.agent_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

    if data.conversation_id:
        conv = await service.get(data.conversation_id)
        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        history = [{"role": m.role.value, "content": m.content} for m in conv.messages]
    else:
        conv = await service.create(user_id=user_id, agent_id=agent_id, title=data.message[:100])
        history = []

    await service.add_message(conv.id, MessageRole.USER, data.message)
    await service.session.commit()
    conv_id = conv.id

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        full_content = ""
        async for event in orchestrator.stream_response(agent_id, data.message, history):
            if event["type"] == "text_delta":
                full_content += event["content"]
            if event["type"] == "done":
                event["conversation_id"] = str(conv_id)
            yield {"event": event["type"], "data": json.dumps(event)}

        async with session_factory() as session:
            svc = ConversationService(session)
            await svc.add_message(conv_id, MessageRole.ASSISTANT, full_content)
            await session.commit()

    return EventSourceResponse(event_generator())


@router.get(
    "/conversations",
    response_model=PaginatedResponse[ConversationResponse],
    summary="List conversations",
    description="Retrieve paginated list of conversations for the authenticated user.",
)
async def list_conversations(
    request: Request,
    service: Annotated[ConversationService, Depends(get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ConversationResponse]:
    user_id = get_user_id(request)
    rows, total = await service.list_for_user(user_id, page=page, page_size=page_size)
    items = []
    for conv, msg_count in rows:
        resp = ConversationResponse.model_validate(conv)
        resp.message_count = msg_count
        items.append(resp)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get conversation",
    description="Retrieve a conversation with full message history.",
    responses={404: {"description": "Conversation not found"}},
)
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


@router.delete(
    "/conversations/{conversation_id}",
    status_code=204,
    summary="Delete conversation",
    description="Permanently delete a conversation and all its messages.",
    responses={404: {"description": "Conversation not found"}},
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    service: Annotated[ConversationService, Depends(get_service)],
) -> None:
    if not await service.delete(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
