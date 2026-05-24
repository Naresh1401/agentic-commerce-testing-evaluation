from __future__ import annotations

import importlib
import logging
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from schemas.tool_schemas import TOOL_SCHEMAS
from tools.common import BackendClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
app = FastAPI(title="Agentic Commerce MCP-Style Tool Server", version="1.0.0")
client = BackendClient()

ROLE_PERMISSIONS = {
    "customer": {"search_products", "check_inventory", "get_price", "apply_coupon", "update_cart", "create_checkout_session", "track_order"},
    "associate": {"search_products", "check_inventory", "get_price", "track_order"},
    "admin": set(TOOL_SCHEMAS),
    "partner_agent": {"search_products", "check_inventory", "get_price"},
}


class ToolCall(BaseModel):
    tool: str
    input: Dict[str, Any]
    role: str = "customer"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tools/list")
def list_tools():
    return {"tools": [{"name": name, **schema} for name, schema in TOOL_SCHEMAS.items()]}


@app.post("/tools/call")
def call_tool(call: ToolCall):
    if call.tool not in TOOL_SCHEMAS:
        raise HTTPException(status_code=404, detail={"code": "TOOL_NOT_FOUND", "message": "Unknown tool"})
    if call.tool not in ROLE_PERMISSIONS.get(call.role, set()):
        raise HTTPException(status_code=403, detail={"code": "TOOL_FORBIDDEN", "message": f"Role {call.role} cannot call {call.tool}"})
    required = TOOL_SCHEMAS[call.tool]["required"]
    missing = [key for key in required if key not in call.input]
    if missing:
        raise HTTPException(status_code=422, detail={"code": "TOOL_INPUT_INVALID", "message": f"Missing fields: {missing}"})
    try:
        module = importlib.import_module(f"tools.{call.tool}")
        output = module.run(client, call.input)
        logging.info({"tool": call.tool, "role": call.role, "success": True})
        return {"tool": call.tool, "risk": TOOL_SCHEMAS[call.tool]["risk"], "ok": True, "output": output}
    except Exception:
        logging.info({"tool": call.tool, "role": call.role, "success": False})
        return {"tool": call.tool, "ok": False, "error": {"code": "TOOL_CALL_FAILED", "message": "Tool call failed safely. Check backend availability and input."}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
