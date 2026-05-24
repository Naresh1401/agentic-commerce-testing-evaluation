from __future__ import annotations
from typing import Any, Dict

def run(client, payload: Dict[str, Any]) -> Dict[str, Any]:
    return client.post("/coupons/apply", {"cart_id": payload["cart_id"], "coupon_code": payload["coupon_code"]})
