from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.store import check_inventory

router = APIRouter(prefix="/inventory", tags=["inventory"])


class InventoryCheckRequest(BaseModel):
    sku: str
    store_id: str


@router.get("/{store_id}/{sku}")
def get_inventory(store_id: str, sku: str):
    return check_inventory(store_id, sku)


@router.post("/check")
def post_inventory(request: InventoryCheckRequest):
    return check_inventory(request.store_id, request.sku)
