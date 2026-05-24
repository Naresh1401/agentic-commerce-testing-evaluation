from __future__ import annotations

import re
from typing import Any


EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+)")
PHONE_RE = re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b")
TOKEN_RE = re.compile(r"tok_[A-Za-z0-9_\-]+")
ADDRESS_RE = re.compile(r"\b\d{2,5}\s+[A-Za-z0-9 .]+\b")


def mask_text(value: str) -> str:
    value = EMAIL_RE.sub(r"\1***\2", value)
    value = PHONE_RE.sub("***-***-****", value)
    value = TOKEN_RE.sub("tok_***", value)
    value = ADDRESS_RE.sub("*** masked address ***", value)
    return value


def mask_pii(payload: Any) -> Any:
    if isinstance(payload, str):
        return mask_text(payload)
    if isinstance(payload, list):
        return [mask_pii(item) for item in payload]
    if isinstance(payload, dict):
        masked = {}
        for key, value in payload.items():
            if key.lower() in {"email", "phone", "address", "payment_token"}:
                masked[key] = mask_pii(str(value))
            else:
                masked[key] = mask_pii(value)
        return masked
    return payload
