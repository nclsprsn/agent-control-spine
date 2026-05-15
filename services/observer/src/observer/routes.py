import uuid
from datetime import datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["observer"])


class AgentEvent(BaseModel):
    agent_id: uuid.UUID
    event_type: str
    data: dict
    timestamp: datetime | None = None


class TraceData(BaseModel):
    trace_id: str
    spans: list[dict]


@router.post("/events", status_code=202)
async def ingest_event(event: AgentEvent, request: Request) -> dict:
    exporter = request.app.state.nats_exporter
    await exporter.publish(f"spine.events.{event.event_type}", event.model_dump(mode="json"))
    return {"status": "accepted"}


@router.post("/traces", status_code=202)
async def ingest_traces(traces: TraceData, request: Request) -> dict:
    exporter = request.app.state.nats_exporter
    await exporter.publish("spine.traces", traces.model_dump(mode="json"))
    return {"status": "accepted"}
