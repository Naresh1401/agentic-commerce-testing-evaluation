from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from app.events.event_bus import event_bus
from app.observability.metrics import metrics
from app.observability.tracing import list_traces

router = APIRouter(tags=["observability"])


@router.get("/metrics")
def get_metrics():
    return metrics.snapshot()


@router.get("/traces")
def get_traces(limit: int = 50):
    return {"items": list_traces(limit)}


@router.get("/events")
def get_events(limit: int = 100):
    return {"items": event_bus.list_events(limit)}


@router.get("/events/replay")
def replay_events(event_type: Optional[str] = None):
    return {"items": event_bus.replay(event_type)}
