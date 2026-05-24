from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_single_agent_calls_tools_for_facts():
    response = client.post("/agent/single", json={"prompt": "Find organic milk under $5 near store_1001."})
    assert response.status_code == 200
    payload = response.json()
    tools = [tool["tool"] for tool in payload["tools_called"]]
    assert "search_products" in tools
    assert "get_price" in tools
    assert "check_inventory" in tools
