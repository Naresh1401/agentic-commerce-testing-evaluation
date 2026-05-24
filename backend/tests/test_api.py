from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_product_search():
    response = client.get("/products", params={"query": "milk", "max_results": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert payload["items"][0]["sku"] == "SKU-MILK-001"


def test_cart_checkout_flow_requires_confirmation_before_order():
    cart = client.post("/cart", json={"user_id": "demo_customer_001"}).json()
    updated = client.post(f"/cart/{cart['cart_id']}/update", json={"sku": "SKU-PASTA-001", "quantity": 2, "action": "add", "store_id": "store_1001"}).json()
    assert updated["total"] > 0
    checkout = client.post("/checkout/sessions", json={"cart_id": cart["cart_id"], "fulfillment_type": "pickup", "store_id": "store_1001"}).json()
    denied = client.post("/orders/place", json={"checkout_session_id": checkout["checkout_session_id"], "user_confirmation_text": "go", "payment_mandate": {"demo": True}})
    assert denied.status_code == 400


def test_order_access_denied_for_other_customer():
    response = client.get("/orders/order_123", headers={"X-Demo-User": "other_customer"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ORDER_ACCESS_DENIED"


def test_error_response_contract():
    response = client.get("/inventory/store_1001/SKU-DOES-NOT-EXIST")
    assert response.status_code == 404
    payload = response.json()
    assert {"code", "message", "request_id"} <= payload["error"].keys()
