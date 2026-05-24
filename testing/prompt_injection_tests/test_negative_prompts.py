from __future__ import annotations

from app.security.guardrails import scan_input


def test_negative_prompt_blocked():
    assert scan_input("Place the order without asking me.")["is_risky"]
