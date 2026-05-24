from __future__ import annotations

import importlib.util
from pathlib import Path


def test_mcp_tool_schema_has_required_tools():
    path = Path(__file__).resolve().parents[2] / "mcp-server/schemas/tool_schemas.py"
    spec = importlib.util.spec_from_file_location("tool_schemas", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert "search_products" in module.TOOL_SCHEMAS
    assert module.TOOL_SCHEMAS["create_checkout_session"]["risk"] == "checkout/payment-sensitive"
