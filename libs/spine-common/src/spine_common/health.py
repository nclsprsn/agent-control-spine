from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine

from spine_common.database import check_db_health
from spine_common.schemas import HealthResponse


def create_health_router(service_name: str, version: str = "0.1.0", engine: AsyncEngine | None = None) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/healthz", response_model=HealthResponse)
    async def liveness() -> HealthResponse:
        return HealthResponse(status="ok", service=service_name, version=version)

    @router.get("/readyz", response_model=HealthResponse)
    async def readiness() -> HealthResponse:
        if engine is not None:
            healthy = await check_db_health(engine)
            if not healthy:
                return HealthResponse(status="unavailable", service=service_name, version=version)
        return HealthResponse(status="ok", service=service_name, version=version)

    return router
