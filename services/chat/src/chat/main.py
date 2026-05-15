from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from chat import routes
from chat.config import ChatSettings
from chat.orchestrator import AgentOrchestrator
from spine_common.database import create_engine, create_session_factory, get_session
from spine_common.health import create_health_router
from spine_common.logging import setup_logging
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry

settings = ChatSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine: AsyncEngine = create_engine(settings.database_url)
    factory = create_session_factory(engine)

    async def session_dependency():  # type: ignore[no-untyped-def]
        async for s in get_session(factory):
            yield s

    routes.get_session = session_dependency  # type: ignore[assignment]

    orchestrator = AgentOrchestrator(
        registry_url=settings.registry_url,
        catalog_url=settings.catalog_url,
    )
    app.state.orchestrator = orchestrator

    app.include_router(create_health_router("chat", engine=engine))
    yield

    await orchestrator.close()
    await engine.dispose()


app = FastAPI(title="Chat Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(routes.router)

setup_logging(settings.log_level, settings.otel_service_name)
setup_telemetry(app, settings.otel_service_name)
