from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


traces: List[Dict[str, Any]] = []


def add_trace(request_id: str, name: str, attrs: Dict[str, Any]) -> Dict[str, Any]:
    trace = {
        "trace_id": request_id,
        "span_id": f"span_{len(traces) + 1:05d}",
        "name": name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attributes": attrs,
    }
    traces.append(trace)
    return trace


def list_traces(limit: int = 100) -> List[Dict[str, Any]]:
    return traces[-limit:]
