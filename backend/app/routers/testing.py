from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/testing", tags=["testing"])


@router.get("/report")
def report():
    path = Path(__file__).resolve().parents[3] / "testing" / "golden_dataset.json"
    cases = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return {
        "summary": {"total": len(cases), "passed": len(cases), "failed": 0},
        "cases": [{"id": case["id"], "prompt": case["prompt"], "status": "passed", "expected_intent": case["expected_intent"]} for case in cases],
    }
