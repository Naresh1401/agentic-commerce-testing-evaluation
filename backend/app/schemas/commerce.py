from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class Product(BaseModel):
    sku: str
    upc: str
    name: str
    brand: str
    category: str
    size: str
    image_url: str
    tags: List[str]


class InventoryResponse(BaseModel):
    sku: str
    store_id: str
    stock_status: str
    quantity_available: int
    fulfillment_options: List[str]


class PriceResponse(BaseModel):
    sku: str
    store_id: str
    base_price: float
    sale_price: float
    loyalty_price: Optional[float] = None
    tax_estimate: float
    currency: str = "USD"


class CartItemRequest(BaseModel):
    sku: str
    quantity: int = Field(ge=0)
    action: str = Field(default="add", pattern="^(add|update|remove)$")
    store_id: str = "store_1001"


class CartCreateRequest(BaseModel):
    user_id: str = "demo_customer_001"


class CouponApplyRequest(BaseModel):
    cart_id: str
    coupon_code: str


class CheckoutCreateRequest(BaseModel):
    cart_id: str
    fulfillment_type: str = Field(pattern="^(pickup|delivery)$")
    store_id: str
    slot: str = "tomorrow_morning"


class PlaceOrderRequest(BaseModel):
    checkout_session_id: str
    user_confirmation_text: str
    payment_mandate: Optional[Dict[str, Any]] = None


class LoginRequest(BaseModel):
    username: str = "demo_customer_001"
    role: str = "customer"


class PartnerARequest(BaseModel):
    itemCode: str
    location: str
    qty: int = Field(ge=1)


class PartnerBRequest(BaseModel):
    product_sku: str
    store: str
    quantity_requested: int = Field(ge=1)


class AgentPrompt(BaseModel):
    prompt: str
    user_id: str = "demo_customer_001"
    cart_id: Optional[str] = None
    store_id: str = "store_1001"
    confirmed: bool = False


class RagQuery(BaseModel):
    query: str
