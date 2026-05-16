from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncEngine

from spine_common.database import check_db_health
from spine_common.schemas import HealthResponse

ReadyProbe = Callable[[], Awaitable[bool]]


def create_health_router(
    service_name: str,
    version: str = "0.1.0",
    engine: AsyncEngine | None = None,
    probes: dict[str, ReadyProbe] | None = None,
) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/healthz", response_model=HealthResponse)
    async def liveness() -> HealthResponse:
        return HealthResponse(status="ok", service=service_name, version=version)

    @router.get("/readyz", response_model=HealthResponse)
    async def readiness(response: Response) -> HealthResponse:
        if engine is not None and not await check_db_health(engine):
            response.status_code = 503
            return HealthResponse(status="unavailable", service=service_name, version=version)
        for name, probe in (probes or {}).items():
            try:
                ok = await probe()
            except Exception:
                ok = False
            if not ok:
                response.status_code = 503
                return HealthResponse(status=f"unavailable:{name}", service=service_name, version=version)
        return HealthResponse(status="ok", service=service_name, version=version)

    return router
