from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from app.services.store import get_price

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/{store_id}/{sku}")
def price_lookup(store_id: str, sku: str, loyalty_id: Optional[str] = None):
    return get_price(store_id, sku, loyalty_id=loyalty_id)
