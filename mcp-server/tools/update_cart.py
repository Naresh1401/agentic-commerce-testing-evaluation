from __future__ import annotations
from typing import Any, Dict

def run(client, payload: Dict[str, Any]) -> Dict[str, Any]:
    return client.post(f"/cart/{payload['cart_id']}/update", {"sku": payload["sku"], "quantity": payload["quantity"], "action": payload["action"], "store_id": payload.get("store_id", "store_1001")})
