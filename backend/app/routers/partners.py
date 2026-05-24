from __future__ import annotations

from fastapi import APIRouter, Depends

from app.orchestration.response_normalizer import normalize_partner_inventory
from app.schemas.commerce import PartnerARequest, PartnerBRequest
from app.security.rbac import require_roles
from app.services.store import check_inventory

router = APIRouter(prefix="/partners", tags=["partners"])


@router.post("/a/inventory")
def partner_a(request: PartnerARequest, user=Depends(require_roles("partner_agent", "admin"))):
    normalized = normalize_partner_inventory(request.model_dump())
    internal = check_inventory(normalized["store_id"], normalized["sku"])
    return {
        "partner": "A",
        "normalized_request": normalized,
        "internal_response": internal,
        "partner_response": {"itemCode": internal["sku"], "location": internal["store_id"], "available": internal["quantity_available"] >= normalized["quantity"]},
    }


@router.post("/b/inventory")
def partner_b(request: PartnerBRequest, user=Depends(require_roles("partner_agent", "admin"))):
    normalized = normalize_partner_inventory(request.model_dump())
    internal = check_inventory(normalized["store_id"], normalized["sku"])
    return {
        "partner": "B",
        "normalized_request": normalized,
        "internal_response": internal,
        "partner_response": {"product_sku": internal["sku"], "store": internal["store_id"], "can_fulfill": internal["quantity_available"] >= normalized["quantity"]},
    }


@router.get("/demo")
def partner_demo():
    request = {"itemCode": "SKU-PASTA-001", "location": "store_1001", "qty": 2}
    normalized = normalize_partner_inventory(request)
    internal = check_inventory(normalized["store_id"], normalized["sku"])
    return {"partner_request": request, "normalized_request": normalized, "internal_response": internal, "partner_response": {"itemCode": internal["sku"], "available": True}}
