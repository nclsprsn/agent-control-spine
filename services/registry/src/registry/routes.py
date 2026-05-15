import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from registry.models import AgentStatus
from registry.schemas import AgentCreate, AgentResponse, AgentUpdate
from registry.service import AgentService
from spine_common.schemas import PaginatedResponse

router = APIRouter(prefix="/v1/agents", tags=["agents"])


async def get_session() -> AsyncSession:  # type: ignore[misc]
    raise NotImplementedError("Overridden at app startup")


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AgentService:
    return AgentService(session)


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    data: AgentCreate,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.create(data)
    return AgentResponse.model_validate(agent)


@router.get("/", response_model=PaginatedResponse[AgentResponse])
async def list_agents(
    service: Annotated[AgentService, Depends(get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: AgentStatus | None = None,
) -> PaginatedResponse[AgentResponse]:
    agents, total = await service.list(page=page, page_size=page_size, status_filter=status)
    return PaginatedResponse(
        items=[AgentResponse.model_validate(a) for a in agents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.get(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.update(agent_id, data)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: uuid.UUID,
    service: Annotated[AgentService, Depends(get_service)],
) -> None:
    deleted = await service.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.post("/{agent_id}/heartbeat", response_model=AgentResponse)
async def heartbeat(
    agent_id: uuid.UUID,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.heartbeat(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)
