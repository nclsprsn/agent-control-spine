from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from spine_common.auth import JWKSCache, install_auth, require_user
from spine_common.database import create_engine, create_session_factory, get_session
from spine_common.health import create_health_router
from spine_common.logging import setup_logging
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry
from sqlalchemy.ext.asyncio import AsyncEngine

from chat import routes
from chat.config import ChatSettings
from chat.langfuse_integration import init_langfuse
from chat.langfuse_integration import shutdown as langfuse_shutdown
from chat.models import Conversation, Message  # noqa: F401 — register models with Base
from chat.orchestrator import AgentOrchestrator

settings = ChatSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine: AsyncEngine = create_engine(settings.database_url)
    factory = create_session_factory(engine)

    async def session_dependency():  # type: ignore[no-untyped-def]
        async for s in get_session(factory):
            yield s

    app.dependency_overrides[routes.get_session] = session_dependency
    app.state.session_factory = factory

    jwks: JWKSCache | None = install_auth(
        app,
        jwks_url=settings.keycloak_jwks_url,
        issuer=settings.keycloak_issuer,
        disabled=settings.auth_disabled,
    )

    init_langfuse(settings)

    orchestrator = AgentOrchestrator(
        registry_url=settings.registry_url,
        catalog_url=settings.catalog_url,
        ollama_url=settings.ollama_base_url,
        model=settings.llm_model,
    )
    app.state.orchestrator = orchestrator

    app.include_router(create_health_router("chat", engine=engine))
    yield

    langfuse_shutdown()
    await orchestrator.close()
    if jwks:
        await jwks.close()
    await engine.dispose()


app = FastAPI(
    title="Chat Service",
    version="0.1.0",
    description="LLM orchestration — SSE streaming chat, conversation management, multi-agent routing.",
    lifespan=lifespan,
    openapi_tags=[{"name": "chat", "description": "Chat streaming and conversation management"}],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(routes.router, dependencies=[Depends(require_user)])

setup_logging(settings.log_level, settings.otel_service_name)
setup_telemetry(app, settings.otel_service_name)
