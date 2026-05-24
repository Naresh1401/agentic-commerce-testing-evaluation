from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.events.producers import emit_commerce_event
from app.observability.metrics import metrics
from app.seed.seed_data import load_sample_data
from app.services.errors import commerce_error


DATA = load_sample_data()
PRODUCTS: Dict[str, Dict[str, Any]] = {product["sku"]: product for product in DATA["products"]}
INVENTORY: Dict[tuple[str, str], Dict[str, Any]] = {
    (row["store_id"], row["sku"]): row for row in DATA["inventory"]
}
COUPONS: Dict[str, Dict[str, Any]] = {coupon["code"]: coupon for coupon in DATA["coupons"]}
CARTS: Dict[str, Dict[str, Any]] = {}
CHECKOUT_SESSIONS: Dict[str, Dict[str, Any]] = {}
ORDERS: Dict[str, Dict[str, Any]] = {order["order_id"]: order for order in DATA["orders"]}


def reset_demo_state() -> None:
    CARTS.clear()
    CHECKOUT_SESSIONS.clear()
    ORDERS.clear()
    for order in DATA["orders"]:
        ORDERS[order["order_id"]] = dict(order)


def product_public(product: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "sku": product["sku"],
        "upc": product["upc"],
        "name": product["name"],
        "brand": product["brand"],
        "category": product["category"],
        "size": product["size"],
        "image_url": product["image_url"],
        "tags": product["tags"],
    }


def search_products(query: Optional[str] = None, category: Optional[str] = None, brand: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
    query_l = (query or "").lower().strip()
    category_l = (category or "").lower().strip()
    brand_l = (brand or "").lower().strip()
    results = []
    for product in PRODUCTS.values():
        haystack = " ".join([product["name"], product["brand"], product["category"], " ".join(product["tags"])]).lower()
        if query_l and query_l not in haystack:
            continue
        if category_l and category_l != product["category"].lower():
            continue
        if brand_l and brand_l not in product["brand"].lower():
            continue
        results.append(product_public(product))
    emit_commerce_event("product_viewed", {"query": query, "result_count": len(results)})
    return results[:max_results]


def get_product(sku: str) -> Dict[str, Any]:
    product = PRODUCTS.get(sku)
    if not product:
        commerce_error(404, "PRODUCT_NOT_FOUND", f"Product {sku} was not found")
    return product_public(product)


def check_inventory(store_id: str, sku: str) -> Dict[str, Any]:
    row = INVENTORY.get((store_id, sku))
    if not row:
        commerce_error(404, "INVENTORY_NOT_FOUND", "Inventory not found for SKU")
    return dict(row)


def get_price(store_id: str, sku: str, loyalty_id: Optional[str] = None) -> Dict[str, Any]:
    product = PRODUCTS.get(sku)
    if not product:
        commerce_error(404, "PRODUCT_NOT_FOUND", f"Product {sku} was not found")
    effective = product["loyalty_price"] if loyalty_id else product["sale_price"]
    tax = round(effective * 0.0725, 2)
    return {
        "sku": sku,
        "store_id": store_id,
        "base_price": product["base_price"],
        "sale_price": product["sale_price"],
        "loyalty_price": product["loyalty_price"] if loyalty_id else None,
        "tax_estimate": tax,
        "currency": "USD",
    }


def create_cart(user_id: str) -> Dict[str, Any]:
    cart_id = "cart_" + uuid4().hex[:10]
    CARTS[cart_id] = {"cart_id": cart_id, "user_id": user_id, "items": [], "coupon_codes": [], "subtotal": 0.0, "discount_total": 0.0, "tax_estimate": 0.0, "total": 0.0}
    emit_commerce_event("cart_updated", {"cart_id": cart_id, "action": "created"})
    return CARTS[cart_id]


def get_or_create_cart(cart_id: Optional[str], user_id: str) -> Dict[str, Any]:
    if cart_id and cart_id in CARTS:
        return CARTS[cart_id]
    return create_cart(user_id)


def get_cart(cart_id: str) -> Dict[str, Any]:
    cart = CARTS.get(cart_id)
    if not cart:
        commerce_error(404, "CART_NOT_FOUND", f"Cart {cart_id} was not found")
    return cart


def recalculate_cart(cart: Dict[str, Any], store_id: str = "store_1001") -> Dict[str, Any]:
    subtotal = 0.0
    tax = 0.0
    normalized_items = []
    for item in cart["items"]:
        product = PRODUCTS[item["sku"]]
        price = get_price(store_id, item["sku"], loyalty_id="demo_loyalty_001")
        line_price = price["loyalty_price"] or price["sale_price"]
        line_total = round(line_price * item["quantity"], 2)
        subtotal += line_total
        tax += price["tax_estimate"] * item["quantity"]
        normalized_items.append({**item, "name": product["name"], "unit_price": line_price, "line_total": line_total})
    cart["items"] = normalized_items
    cart["subtotal"] = round(subtotal, 2)
    discount = 0.0
    for code in cart.get("coupon_codes", []):
        coupon = COUPONS.get(code)
        if coupon and coupon["active"] and subtotal >= coupon["minimum_cart_total"]:
            if coupon["discount_type"] == "percent":
                discount += subtotal * (coupon["discount_value"] / 100)
            else:
                discount += coupon["discount_value"]
    cart["discount_total"] = round(min(discount, subtotal), 2)
    cart["tax_estimate"] = round(tax, 2)
    cart["total"] = round(max(subtotal - cart["discount_total"], 0) + cart["tax_estimate"], 2)
    return cart


def update_cart(cart_id: str, sku: str, quantity: int, action: str = "add", store_id: str = "store_1001", user_id: str = "demo_customer_001") -> Dict[str, Any]:
    if sku not in PRODUCTS:
        commerce_error(404, "PRODUCT_NOT_FOUND", f"Product {sku} was not found")
    cart = get_or_create_cart(cart_id if cart_id != "new" else None, user_id)
    inventory = check_inventory(store_id, sku)
    if action in {"add", "update"} and inventory["quantity_available"] < quantity:
        commerce_error(409, "INSUFFICIENT_INVENTORY", f"Only {inventory['quantity_available']} units available")
    items = [item for item in cart["items"] if item["sku"] != sku]
    existing_qty = next((item["quantity"] for item in cart["items"] if item["sku"] == sku), 0)
    if action == "add":
        new_qty = existing_qty + quantity
        if inventory["quantity_available"] < new_qty:
            commerce_error(409, "INSUFFICIENT_INVENTORY", f"Only {inventory['quantity_available']} units available")
        items.append({"sku": sku, "quantity": new_qty})
    elif action == "update" and quantity > 0:
        items.append({"sku": sku, "quantity": quantity})
    elif action == "remove":
        pass
    cart["items"] = items
    recalculate_cart(cart, store_id)
    emit_commerce_event("cart_updated", {"cart_id": cart["cart_id"], "sku": sku, "quantity": quantity, "action": action})
    return cart


def validate_coupon(code: str, cart_id: Optional[str] = None) -> Dict[str, Any]:
    coupon = COUPONS.get(code.upper())
    if not coupon:
        return {"coupon_code": code, "valid": False, "reason": "Coupon was not found"}
    expires_at = datetime.fromisoformat(coupon["expires_at"].replace("Z", "+00:00"))
    if not coupon["active"] or expires_at < datetime.now(timezone.utc):
        return {"coupon_code": code, "valid": False, "reason": "Coupon is expired or inactive"}
    if cart_id and cart_id in CARTS and CARTS[cart_id]["subtotal"] < coupon["minimum_cart_total"]:
        return {"coupon_code": code, "valid": False, "reason": f"Minimum cart total is {coupon['minimum_cart_total']}"}
    return {"coupon_code": code.upper(), "valid": True, "description": coupon["description"], "discount_type": coupon["discount_type"], "discount_value": coupon["discount_value"]}


def apply_coupon(cart_id: str, coupon_code: str) -> Dict[str, Any]:
    cart = get_cart(cart_id)
    validation = validate_coupon(coupon_code, cart_id)
    if not validation["valid"]:
        commerce_error(400, "COUPON_INVALID", validation["reason"])
    code = coupon_code.upper()
    if code not in cart["coupon_codes"]:
        cart["coupon_codes"].append(code)
    recalculate_cart(cart)
    emit_commerce_event("cart_updated", {"cart_id": cart_id, "coupon_code": code, "action": "coupon_applied"})
    return {"cart": cart, "coupon": validation}


def create_checkout_session(cart_id: str, fulfillment_type: str, store_id: str, slot: str = "tomorrow_morning") -> Dict[str, Any]:
    cart = get_cart(cart_id)
    if not cart["items"]:
        commerce_error(400, "EMPTY_CART", "Cannot create checkout session for empty cart")
    unavailable = []
    for item in cart["items"]:
        inventory = check_inventory(store_id, item["sku"])
        if inventory["quantity_available"] < item["quantity"]:
            unavailable.append(item["sku"])
    if unavailable:
        commerce_error(409, "CHECKOUT_UNAVAILABLE_ITEMS", f"Unavailable SKUs: {', '.join(unavailable)}")
    session_id = "checkout_" + uuid4().hex[:10]
    session = {
        "checkout_session_id": session_id,
        "cart_id": cart_id,
        "user_id": cart["user_id"],
        "fulfillment_type": fulfillment_type,
        "store_id": store_id,
        "slot": slot,
        "status": "requires_confirmation",
        "total": cart["total"],
        "currency": "USD",
        "confirmation_required": True,
    }
    CHECKOUT_SESSIONS[session_id] = session
    metrics.increment("checkout_sessions_created")
    emit_commerce_event("checkout_created", {"checkout_session_id": session_id, "cart_id": cart_id, "total": cart["total"]})
    return session


def place_order(checkout_session_id: str, user_confirmation_text: str, payment_mandate: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    session = CHECKOUT_SESSIONS.get(checkout_session_id)
    if not session:
        commerce_error(404, "CHECKOUT_SESSION_NOT_FOUND", "Checkout session was not found")
    if "confirm" not in user_confirmation_text.lower() and "place order" not in user_confirmation_text.lower():
        commerce_error(400, "CONFIRMATION_REQUIRED", "Explicit user confirmation is required before order placement")
    if payment_mandate is None:
        commerce_error(400, "PAYMENT_MANDATE_REQUIRED", "Payment-sensitive flow requires a demo payment mandate")
    order_id = "order_" + uuid4().hex[:10]
    cart = get_cart(session["cart_id"])
    order = {
        "order_id": order_id,
        "user_id": session["user_id"],
        "cart_id": session["cart_id"],
        "status": "placed",
        "store_id": session["store_id"],
        "total": session["total"],
        "items": [{"sku": item["sku"], "quantity": item["quantity"]} for item in cart["items"]],
        "timeline": [
            {"event": "order_placed", "timestamp": datetime.now(timezone.utc).isoformat()},
        ],
    }
    ORDERS[order_id] = order
    session["status"] = "order_placed"
    metrics.increment("orders_placed")
    emit_commerce_event("payment_authorized", {"order_id": order_id, "amount": session["total"]})
    emit_commerce_event("order_placed", {"order_id": order_id, "cart_id": session["cart_id"]})
    return order


def list_orders_for_user(user_id: str, role: str) -> List[Dict[str, Any]]:
    if role == "admin":
        return list(ORDERS.values())
    return [order for order in ORDERS.values() if order["user_id"] == user_id]


def track_order(order_id: str, user_id: str, role: str) -> Dict[str, Any]:
    order = ORDERS.get(order_id)
    if not order:
        commerce_error(404, "ORDER_NOT_FOUND", f"Order {order_id} was not found")
    if role == "customer" and order["user_id"] != user_id:
        metrics.increment("rbac_denied_count")
        commerce_error(403, "ORDER_ACCESS_DENIED", "Customer can only view their own orders")
    return order


def capstone_demo(user_id: str, store_id: str, confirmed: bool = False) -> Dict[str, Any]:
    desired = ["SKU-PASTA-001", "SKU-SAUCE-001", "SKU-SALAD-001", "SKU-BREAD-001", "SKU-CHEESE-001"]
    cart = create_cart(user_id)
    tool_results = []
    total_limit = 40.0
    for sku in desired:
        inventory = check_inventory(store_id, sku)
        price = get_price(store_id, sku, loyalty_id="demo_loyalty_001")
        tool_results.append({"tool": "check_inventory", "sku": sku, "available": inventory["quantity_available"] > 0})
        if inventory["quantity_available"] > 0:
            update_cart(cart["cart_id"], sku, 1 if sku != "SKU-PASTA-001" else 2, "add", store_id, user_id)
    if cart["subtotal"] >= 20:
        apply_coupon(cart["cart_id"], "SAVE10")
    response = {
        "intent": "meal_planning_cart_checkout",
        "cart": cart,
        "budget_ok": cart["total"] <= total_limit,
        "requires_confirmation": not confirmed,
        "tool_results": tool_results,
        "final_response": "I found available pasta dinner items under $40. Please confirm before I create pickup checkout." if not confirmed else "Confirmed. Pickup checkout session is ready for tomorrow morning.",
    }
    if confirmed:
        response["checkout_session"] = create_checkout_session(cart["cart_id"], "pickup", store_id, "tomorrow_morning")
    return response
