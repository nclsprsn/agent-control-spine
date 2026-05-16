import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from spine_common.schemas import PaginatedResponse
from sqlalchemy.ext.asyncio import AsyncSession

from registry.models import AgentStatus
from registry.schemas import AgentCreate, AgentResponse, AgentUpdate
from registry.service import AgentService

router = APIRouter(prefix="/v1/agents", tags=["agents"])


async def get_session() -> AsyncSession:
    raise NotImplementedError("Overridden at app startup")


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AgentService:
    return AgentService(session)


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=201,
    summary="Register agent",
    description=(
        "Register a new agent with the control plane. "
        "Returns the created agent with assigned ID and initial status."
    ),
    responses={409: {"description": "Agent with same name/version already exists"}},
)
async def create_agent(
    data: AgentCreate,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.create(data)
    return AgentResponse.model_validate(agent)


@router.get(
    "/",
    response_model=PaginatedResponse[AgentResponse],
    summary="List agents",
    description="Retrieve paginated list of registered agents. Optionally filter by status.",
)
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


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get agent",
    description="Retrieve a single agent by ID.",
    responses={404: {"description": "Agent not found"}},
)
async def get_agent(
    agent_id: uuid.UUID,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.get(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.patch(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update agent",
    description="Partially update an agent's fields. Only provided fields are modified.",
    responses={404: {"description": "Agent not found"}},
)
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.update(agent_id, data)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.delete(
    "/{agent_id}",
    status_code=204,
    summary="Delete agent",
    description="Permanently remove an agent from the registry.",
    responses={404: {"description": "Agent not found"}},
)
async def delete_agent(
    agent_id: uuid.UUID,
    service: Annotated[AgentService, Depends(get_service)],
) -> None:
    deleted = await service.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.post(
    "/{agent_id}/heartbeat",
    response_model=AgentResponse,
    summary="Agent heartbeat",
    description="Report agent liveness. Updates last_heartbeat_at and transitions status to active.",
    responses={404: {"description": "Agent not found"}},
)
async def heartbeat(
    agent_id: uuid.UUID,
    service: Annotated[AgentService, Depends(get_service)],
) -> AgentResponse:
    agent = await service.heartbeat(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)
