from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_openapi_exports_contracts():
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert "/products" in openapi.json()["paths"]


def test_inventory_response_contract():
    response = client.get("/inventory/store_1001/SKU-PASTA-001")
    assert response.status_code == 200
    payload = response.json()
    assert {"sku", "store_id", "stock_status", "quantity_available", "fulfillment_options"} <= payload.keys()


def test_checkout_session_contract():
    cart = client.post("/cart", json={"user_id": "demo_customer_001"}).json()
    client.post(f"/cart/{cart['cart_id']}/update", json={"sku": "SKU-SAUCE-001", "quantity": 1, "action": "add", "store_id": "store_1001"})
    response = client.post("/checkout/sessions", json={"cart_id": cart["cart_id"], "fulfillment_type": "pickup", "store_id": "store_1001"})
    assert response.status_code == 200
    assert {"checkout_session_id", "cart_id", "status", "total"} <= response.json().keys()
