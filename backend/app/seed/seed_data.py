from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DATA_PATH = Path(__file__).with_name("sample_data.json")


def load_sample_data() -> Dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    data = load_sample_data()
    print(json.dumps({"products": len(data["products"]), "stores": len(data["stores"]), "inventory_rows": len(data["inventory"])}, indent=2))
