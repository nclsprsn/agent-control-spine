from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from observer.config import ObserverSettings
from observer.exporters import NATSExporter
from observer.routes import router
from spine_common.health import create_health_router
from spine_common.logging import setup_logging
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry

settings = ObserverSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    nats_exporter = NATSExporter()
    try:
        await nats_exporter.connect(settings.nats_url)
    except Exception:
        pass  # NATS optional — service still works without it
    app.state.nats_exporter = nats_exporter

    app.include_router(create_health_router("observer"))
    yield

    await nats_exporter.close()


app = FastAPI(title="Observer Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router)

setup_logging(settings.log_level, settings.otel_service_name)
setup_telemetry(app, settings.otel_service_name)
