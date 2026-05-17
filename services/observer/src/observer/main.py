from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI
from spine_common.auth import JWKSCache, install_auth, require_user
from spine_common.health import create_health_router
from spine_common.logging import setup_logging
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry

from observer.config import ObserverSettings
from observer.exporters import NATSExporter
from observer.routes import router

settings = ObserverSettings()
log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    nats_exporter = NATSExporter()
    try:
        await nats_exporter.connect(settings.nats_url)
    except Exception:
        log.error("nats_connect_failed", nats_url=settings.nats_url, exc_info=True)
    app.state.nats_exporter = nats_exporter

    jwks: JWKSCache | None = install_auth(
        app,
        jwks_url=settings.keycloak_jwks_url,
        issuer=settings.keycloak_issuer,
        disabled=settings.auth_disabled,
    )

    async def nats_ready() -> bool:
        return nats_exporter.is_connected()

    app.include_router(create_health_router("observer", probes={"nats": nats_ready}))
    yield

    if jwks:
        await jwks.close()
    await nats_exporter.close()


app = FastAPI(
    title="Observer Service",
    version="0.1.0",
    description="Observability ingestion — accepts agent events and traces, forwards to NATS/OTel.",
    lifespan=lifespan,
    openapi_tags=[{"name": "observer", "description": "Event and trace ingestion"}],
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router, dependencies=[Depends(require_user)])

setup_logging(settings.log_level, settings.otel_service_name)
setup_telemetry(app, settings.otel_service_name)
