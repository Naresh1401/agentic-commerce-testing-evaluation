from __future__ import annotations

import os
from typing import Any, Dict

import httpx


class BackendClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("MCP_BACKEND_URL", "http://localhost:8000").rstrip("/")
        self.timeout = 4.0

    def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}{path}", params=params)
            response.raise_for_status()
            return response.json()

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}{path}", json=payload)
            response.raise_for_status()
            return response.json()
