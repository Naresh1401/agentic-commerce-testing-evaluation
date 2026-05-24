from __future__ import annotations

from typing import Any, Dict

from app.observability.metrics import metrics
from app.security.pii_masking import mask_pii


PROMPT_INJECTION_PATTERNS = [
    "ignore all previous rules",
    "developer message",
    "system prompt",
    "show me all customer orders",
    "bypass",
    "without asking",
]


def scan_input(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    hits = [pattern for pattern in PROMPT_INJECTION_PATTERNS if pattern in lowered]
    if hits:
        metrics.increment("prompt_injection_attempts")
    return {"is_risky": bool(hits), "matches": hits, "risk_level": "high" if hits else "low"}


def verify_output(payload: Any) -> Any:
    return mask_pii(payload)


def policy_violation_response(reason: str) -> Dict[str, Any]:
    return {
        "blocked": True,
        "reason": reason,
        "message": "I cannot perform that request in the demo because it violates commerce safety or data access policy.",
    }
