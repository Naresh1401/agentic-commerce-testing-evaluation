from __future__ import annotations

from typing import Any, Dict

from app.security.guardrails import policy_violation_response, scan_input
from app.services.store import capstone_demo


def orchestrate_capstone(prompt: str, user_id: str, store_id: str, confirmed: bool = False) -> Dict[str, Any]:
    risk = scan_input(prompt)
    if risk["is_risky"]:
        return {
            "intent": "blocked",
            "risk": risk,
            "requires_confirmation": False,
            "final_response": policy_violation_response("prompt_injection")["message"],
            "tool_results": [],
        }
    return capstone_demo(user_id=user_id, store_id=store_id, confirmed=confirmed)
