import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from spine_common.health import create_health_router
from spine_common.logging import setup_logging
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry

from observer.config import ObserverSettings
from observer.exporters import NATSExporter
from observer.routes import router

settings = ObserverSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    nats_exporter = NATSExporter()
    with contextlib.suppress(Exception):
        await nats_exporter.connect(settings.nats_url)
    app.state.nats_exporter = nats_exporter

    app.include_router(create_health_router("observer"))
    yield

    await nats_exporter.close()


app = FastAPI(
    title="Observer Service",
    version="0.1.0",
    description="Observability ingestion — accepts agent events and traces, forwards to NATS/OTel.",
    lifespan=lifespan,
    openapi_tags=[{"name": "observer", "description": "Event and trace ingestion"}],
)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router)

setup_logging(settings.log_level, settings.otel_service_name)
setup_telemetry(app, settings.otel_service_name)
