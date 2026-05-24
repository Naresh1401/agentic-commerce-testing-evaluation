from __future__ import annotations

from fastapi import APIRouter

from app.schemas.commerce import CheckoutCreateRequest
from app.services.store import create_checkout_session

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/sessions")
def create_session(request: CheckoutCreateRequest):
    return create_checkout_session(request.cart_id, request.fulfillment_type, request.store_id, request.slot)
