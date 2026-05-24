from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.commerce import CouponApplyRequest
from app.services.store import apply_coupon, validate_coupon

router = APIRouter(prefix="/coupons", tags=["coupons"])


class CouponValidateRequest(BaseModel):
    coupon_code: str
    cart_id: str | None = None


@router.post("/validate")
def validate(request: CouponValidateRequest):
    return validate_coupon(request.coupon_code, request.cart_id)


@router.post("/apply")
def apply(request: CouponApplyRequest):
    return apply_coupon(request.cart_id, request.coupon_code)
