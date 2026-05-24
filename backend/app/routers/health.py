from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "agentic-commerce-backend"}


@router.get("/ready")
def ready():
    return {"status": "ready", "dependencies": {"database": "mock-ready", "redis": "mock-ready"}}
