from __future__ import annotations

from typing import Any, Dict


def normalize_partner_inventory(payload: Dict[str, Any]) -> Dict[str, Any]:
    if {"itemCode", "location", "qty"}.issubset(payload):
        return {"sku": payload["itemCode"], "store_id": payload["location"], "quantity": payload["qty"]}
    if {"product_sku", "store", "quantity_requested"}.issubset(payload):
        return {"sku": payload["product_sku"], "store_id": payload["store"], "quantity": payload["quantity_requested"]}
    return payload


def normalize_error(code: str, message: str) -> Dict[str, Any]:
    return {"error": {"code": code, "message": message}}
