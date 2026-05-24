from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.commerce import LoginRequest
from app.security.auth import AUDIT_LOG, audit, create_access_token, get_current_user
from app.security.rbac import require_roles

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(request: LoginRequest):
    token = create_access_token(request.username, request.role)
    audit("login", {"user_id": request.username, "role": request.role})
    return {"access_token": token, "token_type": "bearer", "role": request.role, "user_id": request.username}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


@router.get("/audit-log")
def audit_log(user=Depends(require_roles("admin"))):
    return {"items": AUDIT_LOG}
