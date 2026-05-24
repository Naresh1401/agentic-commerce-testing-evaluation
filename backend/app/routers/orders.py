from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.commerce import PlaceOrderRequest
from app.security.auth import get_current_user
from app.services.store import list_orders_for_user, place_order, track_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders(user=Depends(get_current_user)):
    return {"items": list_orders_for_user(user["user_id"], user["role"])}


@router.get("/{order_id}")
def get_order(order_id: str, user=Depends(get_current_user)):
    return track_order(order_id, user["user_id"], user["role"])


@router.post("/place")
def place(request: PlaceOrderRequest, user=Depends(get_current_user)):
    return place_order(request.checkout_session_id, request.user_confirmation_text, request.payment_mandate)
