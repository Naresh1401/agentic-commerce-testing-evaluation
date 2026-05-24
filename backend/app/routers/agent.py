from __future__ import annotations

from fastapi import APIRouter

from app.observability.metrics import metrics
from app.schemas.commerce import AgentPrompt
from app.security.guardrails import policy_violation_response, scan_input
from app.services.store import capstone_demo, check_inventory, create_checkout_session, get_or_create_cart, get_price, search_products, track_order, update_cart, validate_coupon

router = APIRouter(prefix="/agent", tags=["agents"])


def _resolve_sku_by_text(text: str):
    lowered = text.lower()
    mapping = {
        "banana": "SKU-BANANA-001",
        "pasta sauce": "SKU-SAUCE-001",
        "sauce": "SKU-SAUCE-001",
        "milk": "SKU-MILK-001",
        "cereal": "SKU-CEREAL-001",
        "pasta": "SKU-PASTA-001",
    }
    return [sku for key, sku in mapping.items() if key in lowered]


@router.post("/single")
def single_agent(request: AgentPrompt):
    risk = scan_input(request.prompt)
    if risk["is_risky"]:
        return {"intent": "blocked", "tools_called": [], "requires_confirmation": False, "final_response": policy_violation_response("prompt_injection")["message"], "risk": risk}
    lowered = request.prompt.lower()
    tools = []
    if "track" in lowered and "order_" in lowered:
        order_id = lowered.split("order_")[1].split()[0]
        result = track_order("order_" + order_id, request.user_id, "customer")
        tools.append({"tool": "track_order", "input": {"order_id": result["order_id"]}, "output": result})
        return {"intent": "order_tracking", "tools_called": tools, "requires_confirmation": False, "final_response": f"Order {result['order_id']} is {result['status']}."}
    if "checkout" in lowered:
        cart = get_or_create_cart(request.cart_id, request.user_id)
        if not request.confirmed:
            return {"intent": "checkout", "tools_called": [], "requires_confirmation": True, "final_response": "Please confirm before I create a checkout session."}
        session = create_checkout_session(cart["cart_id"], "pickup", request.store_id, "tomorrow_morning")
        tools.append({"tool": "create_checkout_session", "input": {"cart_id": cart["cart_id"]}, "output": session})
        return {"intent": "checkout", "tools_called": tools, "requires_confirmation": False, "final_response": "Pickup checkout session is ready for tomorrow morning."}
    if "add" in lowered:
        cart = get_or_create_cart(request.cart_id, request.user_id)
        sku_list = _resolve_sku_by_text(lowered)
        if not request.confirmed:
            return {"intent": "cart_update", "tools_called": [{"tool": "search_products", "output": sku_list}], "requires_confirmation": True, "final_response": "I found the matching products. Please confirm before I update your cart."}
        for sku in sku_list:
            qty = 2 if "two" in lowered and sku == "SKU-BANANA-001" else 1
            output = update_cart(cart["cart_id"], sku, qty, "add", request.store_id, request.user_id)
            tools.append({"tool": "update_cart", "input": {"sku": sku, "quantity": qty}, "output": output})
        return {"intent": "cart_update", "tools_called": tools, "requires_confirmation": False, "final_response": f"Updated cart {cart['cart_id']}."}
    if "coupon" in lowered or "sale" in lowered:
        products = search_products(query="cereal", max_results=3)
        tools.append({"tool": "search_products", "input": {"query": "cereal"}, "output": products})
        if products:
            price = get_price(request.store_id, products[0]["sku"], "demo_loyalty_001")
            tools.append({"tool": "get_price", "input": {"sku": products[0]["sku"]}, "output": price})
        coupon = validate_coupon("SAVE10")
        tools.append({"tool": "validate_coupon", "input": {"coupon_code": "SAVE10"}, "output": coupon})
        return {"intent": "pricing_coupon", "tools_called": tools, "requires_confirmation": False, "final_response": "Cereal pricing was checked through the API; SAVE10 is valid for eligible carts."}
    products = search_products(query="organic milk", category="dairy", max_results=5)
    tools.append({"tool": "search_products", "input": {"query": "organic milk"}, "output": products})
    filtered = []
    for product in products:
        price = get_price(request.store_id, product["sku"], "demo_loyalty_001")
        inventory = check_inventory(request.store_id, product["sku"])
        tools.append({"tool": "get_price", "input": {"sku": product["sku"]}, "output": price})
        tools.append({"tool": "check_inventory", "input": {"sku": product["sku"]}, "output": inventory})
        if (price["loyalty_price"] or price["sale_price"]) < 5 and inventory["quantity_available"] > 0:
            filtered.append(product)
    return {"intent": "product_search", "tools_called": tools, "requires_confirmation": False, "final_response": f"Found {len(filtered)} matching organic milk item(s) under $5 near {request.store_id}.", "products": filtered}


@router.post("/multi")
def multi_agent(request: AgentPrompt):
    metrics.increment("simulated_token_usage", 640)
    return capstone_demo(request.user_id, request.store_id, request.confirmed)


@router.post("/capstone")
def capstone(request: AgentPrompt):
    metrics.increment("simulated_token_usage", 900)
    return capstone_demo(request.user_id, request.store_id, request.confirmed)
