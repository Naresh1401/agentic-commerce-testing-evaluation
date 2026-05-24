from __future__ import annotations
from typing import Any, Dict

def run(client, payload: Dict[str, Any]) -> Dict[str, Any]:
    return client.post("/checkout/sessions", {"cart_id": payload["cart_id"], "fulfillment_type": payload["fulfillment_type"], "store_id": payload["store_id"], "slot": payload.get("slot", "tomorrow_morning")})
