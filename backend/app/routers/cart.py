from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.commerce import CartCreateRequest, CartItemRequest
from app.security.auth import get_current_user
from app.services.store import create_cart, get_cart, update_cart

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("")
def create(request: CartCreateRequest, user=Depends(get_current_user)):
    return create_cart(request.user_id or user["user_id"])


@router.get("/{cart_id}")
def view(cart_id: str, user=Depends(get_current_user)):
    cart = get_cart(cart_id)
    if user["role"] == "customer" and cart["user_id"] != user["user_id"]:
        from app.services.errors import commerce_error
        commerce_error(403, "CART_ACCESS_DENIED", "Customer can only view their own cart")
    return cart


@router.post("/{cart_id}/items")
def add_item(cart_id: str, request: CartItemRequest, user=Depends(get_current_user)):
    return update_cart(cart_id, request.sku, request.quantity, request.action, request.store_id, user["user_id"])


@router.patch("/{cart_id}/items/{sku}")
def patch_item(cart_id: str, sku: str, request: CartItemRequest, user=Depends(get_current_user)):
    return update_cart(cart_id, sku, request.quantity, "update", request.store_id, user["user_id"])


@router.delete("/{cart_id}/items/{sku}")
def remove_item(cart_id: str, sku: str, user=Depends(get_current_user)):
    return update_cart(cart_id, sku, 0, "remove", user_id=user["user_id"])


@router.post("/{cart_id}/update")
def update(cart_id: str, request: CartItemRequest, user=Depends(get_current_user)):
    return update_cart(cart_id, request.sku, request.quantity, request.action, request.store_id, user["user_id"])
