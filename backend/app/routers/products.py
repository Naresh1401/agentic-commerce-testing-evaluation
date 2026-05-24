from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.services.store import get_product, search_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def search(query: Optional[str] = None, category: Optional[str] = None, brand: Optional[str] = None, max_results: int = Query(10, ge=1, le=50)):
    items = search_products(query=query, category=category, brand=brand, max_results=max_results)
    return {"items": items, "count": len(items)}


@router.get("/{sku}")
def product_detail(sku: str):
    return get_product(sku)
