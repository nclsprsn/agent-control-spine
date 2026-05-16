import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from spine_common.schemas import PaginatedResponse
from sqlalchemy.ext.asyncio import AsyncSession

from catalog.schemas import (
    CapabilityCreate,
    CapabilityResponse,
    CapabilityUpdate,
    ToolCreate,
    ToolResponse,
    ToolUpdate,
)
from catalog.service import CatalogService

router = APIRouter(prefix="/v1/catalog", tags=["catalog"])


async def get_session() -> AsyncSession:
    raise NotImplementedError("Overridden at app startup")


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> CatalogService:
    return CatalogService(session)


@router.post(
    "/capabilities",
    response_model=CapabilityResponse,
    status_code=201,
    summary="Create capability",
    description="Register a new agent capability. Optionally link to an agent via agent_id.",
)
async def create_capability(
    data: CapabilityCreate, service: Annotated[CatalogService, Depends(get_service)]
) -> CapabilityResponse:
    cap = await service.create_capability(data)
    return CapabilityResponse.model_validate(cap)


@router.get(
    "/capabilities",
    response_model=PaginatedResponse[CapabilityResponse],
    summary="List capabilities",
    description="Retrieve paginated list of capabilities. Optionally filter by tags.",
)
async def list_capabilities(
    service: Annotated[CatalogService, Depends(get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: list[str] | None = Query(None),
) -> PaginatedResponse[CapabilityResponse]:
    caps, total = await service.list_capabilities(page=page, page_size=page_size, tags=tags)
    return PaginatedResponse(
        items=[CapabilityResponse.model_validate(c) for c in caps],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/capabilities/{cap_id}",
    response_model=CapabilityResponse,
    summary="Get capability",
    description="Retrieve a single capability by ID.",
    responses={404: {"description": "Capability not found"}},
)
async def get_capability(
    cap_id: uuid.UUID, service: Annotated[CatalogService, Depends(get_service)]
) -> CapabilityResponse:
    cap = await service.get_capability(cap_id)
    if cap is None:
        raise HTTPException(status_code=404, detail="Capability not found")
    return CapabilityResponse.model_validate(cap)


@router.patch(
    "/capabilities/{cap_id}",
    response_model=CapabilityResponse,
    summary="Update capability",
    description="Partially update a capability's fields.",
    responses={404: {"description": "Capability not found"}},
)
async def update_capability(
    cap_id: uuid.UUID, data: CapabilityUpdate, service: Annotated[CatalogService, Depends(get_service)]
) -> CapabilityResponse:
    cap = await service.update_capability(cap_id, data)
    if cap is None:
        raise HTTPException(status_code=404, detail="Capability not found")
    return CapabilityResponse.model_validate(cap)


@router.delete(
    "/capabilities/{cap_id}",
    status_code=204,
    summary="Delete capability",
    description="Permanently remove a capability from the catalog.",
    responses={404: {"description": "Capability not found"}},
)
async def delete_capability(cap_id: uuid.UUID, service: Annotated[CatalogService, Depends(get_service)]) -> None:
    if not await service.delete_capability(cap_id):
        raise HTTPException(status_code=404, detail="Capability not found")


@router.post(
    "/tools",
    response_model=ToolResponse,
    status_code=201,
    summary="Create tool",
    description="Register a new tool in the catalog.",
)
async def create_tool(data: ToolCreate, service: Annotated[CatalogService, Depends(get_service)]) -> ToolResponse:
    tool = await service.create_tool(data)
    return ToolResponse.model_validate(tool)


@router.get(
    "/tools",
    response_model=PaginatedResponse[ToolResponse],
    summary="List tools",
    description="Retrieve paginated list of tools. Optionally filter by tags.",
)
async def list_tools(
    service: Annotated[CatalogService, Depends(get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: list[str] | None = Query(None),
) -> PaginatedResponse[ToolResponse]:
    tools, total = await service.list_tools(page=page, page_size=page_size, tags=tags)
    return PaginatedResponse(
        items=[ToolResponse.model_validate(t) for t in tools],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/tools/{tool_id}",
    response_model=ToolResponse,
    summary="Get tool",
    description="Retrieve a single tool by ID.",
    responses={404: {"description": "Tool not found"}},
)
async def get_tool(tool_id: uuid.UUID, service: Annotated[CatalogService, Depends(get_service)]) -> ToolResponse:
    tool = await service.get_tool(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return ToolResponse.model_validate(tool)


@router.patch(
    "/tools/{tool_id}",
    response_model=ToolResponse,
    summary="Update tool",
    description="Partially update a tool's fields.",
    responses={404: {"description": "Tool not found"}},
)
async def update_tool(
    tool_id: uuid.UUID, data: ToolUpdate, service: Annotated[CatalogService, Depends(get_service)]
) -> ToolResponse:
    tool = await service.update_tool(tool_id, data)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return ToolResponse.model_validate(tool)


@router.delete(
    "/tools/{tool_id}",
    status_code=204,
    summary="Delete tool",
    description="Permanently remove a tool from the catalog.",
    responses={404: {"description": "Tool not found"}},
)
async def delete_tool(tool_id: uuid.UUID, service: Annotated[CatalogService, Depends(get_service)]) -> None:
    if not await service.delete_tool(tool_id):
        raise HTTPException(status_code=404, detail="Tool not found")


@router.get(
    "/search",
    summary="Search catalog",
    description="Full-text search across capabilities and tools. Returns matching items from both collections.",
)
async def search_catalog(
    service: Annotated[CatalogService, Depends(get_service)],
    q: str = Query(..., min_length=1),
    tags: list[str] | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    results = await service.search(query=q, tags=tags, page=page, page_size=page_size)
    return {
        "capabilities": [CapabilityResponse.model_validate(c) for c in results["capabilities"]],
        "tools": [ToolResponse.model_validate(t) for t in results["tools"]],
    }
