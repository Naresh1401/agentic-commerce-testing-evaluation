from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

from fastapi import Header, HTTPException

from app.config import settings


AUDIT_LOG: list[dict[str, Any]] = []


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def create_access_token(user_id: str, role: str, expires_in: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": user_id, "role": role, "exp": int(time.time()) + expires_in, "iss": "agentic-commerce-demo"}
    segments = [_b64(json.dumps(header, separators=(",", ":")).encode()), _b64(json.dumps(payload, separators=(",", ":")).encode())]
    signing_input = ".".join(segments).encode()
    sig = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    return ".".join(segments + [_b64(sig)])


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected = _b64(hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest())
        if not hmac.compare_digest(expected, sig_b64):
            raise ValueError("bad signature")
        payload = json.loads(_unb64(payload_b64))
        if payload.get("exp", 0) < time.time():
            raise ValueError("expired")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"}) from exc


def audit(action: str, actor: Dict[str, Any], target: Dict[str, Any] | None = None) -> None:
    AUDIT_LOG.append({"action": action, "actor": actor, "target": target or {}, "timestamp": int(time.time())})


def get_current_user(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    x_demo_role: str | None = Header(default=None),
    x_demo_user: str | None = Header(default=None),
) -> Dict[str, Any]:
    if authorization and authorization.startswith("Bearer "):
        payload = decode_access_token(authorization.removeprefix("Bearer ").strip())
        return {"user_id": payload["sub"], "role": payload["role"], "claims": payload}
    if x_api_key:
        if x_api_key != settings.partner_api_key:
            raise HTTPException(status_code=401, detail={"code": "INVALID_API_KEY", "message": "Partner API key is invalid"})
        return {"user_id": "partner_demo", "role": "partner_agent", "claims": {"partner": True}}
    return {"user_id": x_demo_user or settings.default_user_id, "role": x_demo_role or "customer", "claims": {"demo": True}}
