from __future__ import annotations

from typing import Any, Dict

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "search_products": {"required": ["query"], "risk": "read-only"},
    "check_inventory": {"required": ["sku", "store_id"], "risk": "read-only"},
    "get_price": {"required": ["sku", "store_id"], "risk": "read-only"},
    "apply_coupon": {"required": ["cart_id", "coupon_code"], "risk": "cart-modifying"},
    "update_cart": {"required": ["cart_id", "sku", "quantity", "action"], "risk": "cart-modifying"},
    "create_checkout_session": {"required": ["cart_id", "fulfillment_type", "store_id"], "risk": "checkout/payment-sensitive"},
    "track_order": {"required": ["order_id"], "risk": "read-only"},
}
