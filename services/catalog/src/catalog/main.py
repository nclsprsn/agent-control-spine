from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from spine_common.database import create_engine, create_session_factory, get_session
from spine_common.health import create_health_router
from spine_common.logging import setup_logging
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry
from spine_common.models import Base
from sqlalchemy.ext.asyncio import AsyncEngine

from catalog import routes
from catalog.config import CatalogSettings
from catalog.models import Capability, Tool  # noqa: F401 — register models with Base

settings = CatalogSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine: AsyncEngine = create_engine(settings.database_url)
    factory = create_session_factory(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def session_dependency():  # type: ignore[no-untyped-def]
        async for s in get_session(factory):
            yield s

    app.dependency_overrides[routes.get_session] = session_dependency

    app.include_router(create_health_router("catalog", engine=engine))
    yield
    await engine.dispose()


app = FastAPI(
    title="Agent Catalog",
    version="0.1.0",
    description="Capability and tool discovery — register, search, and manage agent capabilities and tools.",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "catalog", "description": "Capability and tool CRUD, full-text search"},
    ],
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(routes.router)

setup_logging(settings.log_level, settings.otel_service_name)
setup_telemetry(app, settings.otel_service_name)
