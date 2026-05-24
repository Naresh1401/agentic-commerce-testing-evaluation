from __future__ import annotations
from typing import Any, Dict

def run(client, payload: Dict[str, Any]) -> Dict[str, Any]:
    return client.get(f"/pricing/{payload['store_id']}/{payload['sku']}", {"loyalty_id": payload.get("loyalty_id")})
