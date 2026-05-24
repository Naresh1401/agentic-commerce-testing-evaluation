from __future__ import annotations

from typing import Dict, Iterable, Set

from fastapi import Depends, HTTPException

from app.observability.metrics import metrics
from app.security.auth import get_current_user


TOOL_PERMISSIONS: Dict[str, Set[str]] = {
    "search_products": {"customer", "associate", "admin", "partner_agent"},
    "check_inventory": {"customer", "associate", "admin", "partner_agent"},
    "get_price": {"customer", "associate", "admin", "partner_agent"},
    "apply_coupon": {"customer", "admin"},
    "update_cart": {"customer", "admin"},
    "create_checkout_session": {"customer", "admin"},
    "track_order": {"customer", "associate", "admin"},
    "place_order": {"customer", "admin"},
    "admin_read_all_orders": {"admin"},
}


def role_allowed(role: str, allowed: Iterable[str]) -> bool:
    return role in set(allowed) or role == "admin"


def require_roles(*roles: str):
    def dependency(user=Depends(get_current_user)):
        if not role_allowed(user["role"], roles):
            metrics.increment("rbac_denied_count")
            raise HTTPException(status_code=403, detail={"code": "RBAC_DENIED", "message": "Role is not allowed for this operation"})
        return user

    return dependency


def can_call_tool(role: str, tool_name: str) -> bool:
    return role_allowed(role, TOOL_PERMISSIONS.get(tool_name, set()))


def enforce_tool_permission(role: str, tool_name: str) -> None:
    if not can_call_tool(role, tool_name):
        metrics.increment("rbac_denied_count")
        raise HTTPException(status_code=403, detail={"code": "TOOL_FORBIDDEN", "message": f"Role {role} cannot call {tool_name}"})
