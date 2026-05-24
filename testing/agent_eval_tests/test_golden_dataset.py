from __future__ import annotations

import json
from pathlib import Path


def test_golden_dataset_has_twenty_cases():
    data = json.loads((Path(__file__).resolve().parents[1] / "golden_dataset.json").read_text(encoding="utf-8"))
    assert len(data) >= 20
    assert all("requires_confirmation" in case for case in data)
