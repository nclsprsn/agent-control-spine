"""Unit tests for /metrics endpoint exposed by setup_telemetry."""

import pytest
from fastapi import FastAPI
from spine_common.middleware import CorrelationIdMiddleware, setup_telemetry
from starlette.testclient import TestClient


@pytest.fixture
def instrumented_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)
    setup_telemetry(app, service_name="test-service")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/api/v1/test")
    def test_route():
        return {"data": "ok"}

    return app


def test_metrics_endpoint_exposed(instrumented_app: FastAPI) -> None:
    client = TestClient(instrumented_app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]


def test_metrics_contains_http_requests_total(instrumented_app: FastAPI) -> None:
    client = TestClient(instrumented_app)
    client.get("/api/v1/test")
    resp = client.get("/metrics")
    assert "http_requests_total" in resp.text


def test_metrics_excludes_health_paths(instrumented_app: FastAPI) -> None:
    client = TestClient(instrumented_app)
    for _ in range(3):
        client.get("/healthz")
    resp = client.get("/metrics")
    text = resp.text
    assert 'handler="/healthz"' not in text
    assert 'handler="/metrics"' not in text


def test_correlation_id_middleware(instrumented_app: FastAPI) -> None:
    client = TestClient(instrumented_app)
    resp = client.get("/api/v1/test")
    assert "x-request-id" in resp.headers


def test_correlation_id_forwarded(instrumented_app: FastAPI) -> None:
    client = TestClient(instrumented_app)
    resp = client.get("/api/v1/test", headers={"x-request-id": "test-id-123"})
    assert resp.headers["x-request-id"] == "test-id-123"
