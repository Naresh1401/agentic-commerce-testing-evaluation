from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


class InMemoryEventBus:
    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def publish(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_id": "evt_" + uuid4().hex[:12],
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self.events.append(event)
        return event

    def list_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.events[-limit:]

    def replay(self, event_type: str | None = None) -> List[Dict[str, Any]]:
        return [event for event in self.events if event_type is None or event["event_type"] == event_type]


event_bus = InMemoryEventBus()
