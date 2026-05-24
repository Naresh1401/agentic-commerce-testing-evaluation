from __future__ import annotations

from typing import Any, Dict, List

from app.events.event_bus import event_bus


def consume_events(limit: int = 100) -> List[Dict[str, Any]]:
    return event_bus.list_events(limit=limit)
