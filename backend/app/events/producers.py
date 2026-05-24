from __future__ import annotations

from typing import Any, Dict

from app.events.event_bus import event_bus


def emit_commerce_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return event_bus.publish(event_type, payload)
