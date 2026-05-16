import uuid
from datetime import UTC, datetime

import httpx
import pytest
from observer.routes import AgentEvent, TraceData
from pydantic import ValidationError

# --- Unit Tests ---


def test_agent_event_schema():
    event = AgentEvent(
        agent_id=uuid.uuid4(),
        event_type="heartbeat",
        data={"status": "active"},
    )
    assert event.event_type == "heartbeat"
    assert event.timestamp is None


def test_agent_event_with_timestamp():
    ts = datetime.now(tz=UTC)
    event = AgentEvent(
        agent_id=uuid.uuid4(),
        event_type="error",
        data={"message": "timeout"},
        timestamp=ts,
    )
    assert event.timestamp == ts


def test_trace_data_schema():
    trace = TraceData(
        trace_id="abc123",
        spans=[{"name": "handler", "duration_ms": 42}],
    )
    assert trace.trace_id == "abc123"
    assert len(trace.spans) == 1


def test_agent_event_requires_fields():
    with pytest.raises(ValidationError):
        AgentEvent(event_type="x", data={})  # type: ignore[call-arg]


# --- Integration Tests ---


@pytest.mark.integration
async def test_ingest_event(authed_client: httpx.AsyncClient, observer_url: str, require_stack):
    resp = await authed_client.post(
        f"{observer_url}/v1/events",
        json={
            "agent_id": str(uuid.uuid4()),
            "event_type": "test_event",
            "data": {"key": "value"},
        },
    )
    assert resp.status_code == 202
    assert resp.json()["status"] == "accepted"


@pytest.mark.integration
async def test_ingest_traces(authed_client: httpx.AsyncClient, observer_url: str, require_stack):
    resp = await authed_client.post(
        f"{observer_url}/v1/traces",
        json={
            "trace_id": "trace-001",
            "spans": [{"name": "test-span", "duration_ms": 10}],
        },
    )
    assert resp.status_code == 202
    assert resp.json()["status"] == "accepted"


@pytest.mark.integration
async def test_observer_healthz(http_client: httpx.AsyncClient, observer_url: str, require_stack):
    resp = await http_client.get(f"{observer_url}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_observer_readyz(http_client: httpx.AsyncClient, observer_url: str, require_stack):
    resp = await http_client.get(f"{observer_url}/readyz")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_ingest_event_invalid(authed_client: httpx.AsyncClient, observer_url: str, require_stack):
    resp = await authed_client.post(
        f"{observer_url}/v1/events",
        json={"event_type": "missing_agent_id"},
    )
    assert resp.status_code == 422


@pytest.mark.integration
async def test_ingest_traces_invalid(authed_client: httpx.AsyncClient, observer_url: str, require_stack):
    resp = await authed_client.post(
        f"{observer_url}/v1/traces",
        json={"spans": []},
    )
    assert resp.status_code == 422
