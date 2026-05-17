import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from spine_common.auth import Principal, require_user

router = APIRouter(prefix="/v1", tags=["observer"])


class AgentEvent(BaseModel):
    """Agent lifecycle or runtime event."""

    agent_id: uuid.UUID = Field(description="Agent that emitted this event")
    event_type: str = Field(description="Event type (e.g. 'heartbeat', 'error', 'task_complete')")
    data: dict[str, Any] = Field(description="Event payload")
    timestamp: datetime | None = Field(default=None, description="Event timestamp (server-assigned if null)")


class TraceData(BaseModel):
    """OpenTelemetry-compatible trace data."""

    trace_id: str = Field(description="W3C trace ID")
    spans: list[dict[str, Any]] = Field(description="Span records")


@router.post(
    "/events",
    status_code=202,
    summary="Ingest event",
    description="Accept an agent event and forward to NATS for downstream processing. Returns 202 immediately.",
)
async def ingest_event(
    event: AgentEvent,
    request: Request,
    principal: Annotated[Principal, Depends(require_user)],
) -> dict[str, Any]:
    exporter = request.app.state.nats_exporter
    payload = event.model_dump(mode="json") | {"user_id": principal.sub}
    await exporter.publish(f"spine.events.{event.event_type}", payload)
    return {"status": "accepted"}


@router.post(
    "/traces",
    status_code=202,
    summary="Ingest traces",
    description="Accept OpenTelemetry-compatible trace data and forward to NATS/OTel collector.",
)
async def ingest_traces(
    traces: TraceData,
    request: Request,
    principal: Annotated[Principal, Depends(require_user)],
) -> dict[str, Any]:
    exporter = request.app.state.nats_exporter
    payload = traces.model_dump(mode="json") | {"user_id": principal.sub}
    await exporter.publish("spine.traces", payload)
    return {"status": "accepted"}
