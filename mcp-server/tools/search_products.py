from __future__ import annotations
from typing import Any, Dict

def run(client, payload: Dict[str, Any]) -> Dict[str, Any]:
    return client.get("/products", {"query": payload.get("query"), "category": payload.get("category"), "max_results": payload.get("max_results", 5)})
