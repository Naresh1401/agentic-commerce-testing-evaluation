from __future__ import annotations

import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.observability.logging import configure_logging
from app.observability.metrics import metrics
from app.observability.tracing import add_trace
from app.routers import agent, auth, cart, checkout, coupons, health, inventory, metrics as metrics_router, orders, partners, pricing, products, rag, security_demo, testing


configure_logging()
RATE_LIMIT_BUCKET: dict[str, int] = {}
RATE_LIMIT_MAX_REQUESTS = 1000

app = FastAPI(
    title="Agentic Commerce Platform",
    version="1.0.0",
    description="Mock Kroger-style grocery commerce APIs for agentic commerce training. No real customer, payment, or partner data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or "req_" + uuid4().hex[:12]
    request.state.request_id = request_id
    client_host = request.client.host if request.client else "unknown"
    RATE_LIMIT_BUCKET[client_host] = RATE_LIMIT_BUCKET.get(client_host, 0) + 1
    if RATE_LIMIT_BUCKET[client_host] > RATE_LIMIT_MAX_REQUESTS:
        metrics.increment("rate_limited_count")
        return JSONResponse(status_code=429, content={"error": {"code": "RATE_LIMITED", "message": "Demo rate limit exceeded", "request_id": request_id}})
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000
    metrics.record_request(request.url.path, request.method, response.status_code, latency_ms)
    add_trace(request_id, f"{request.method} {request.url.path}", {"status_code": response.status_code, "latency_ms": round(latency_ms, 2)})
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": str(exc.errors()), "request_id": request_id}})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    detail = exc.detail if isinstance(exc.detail, dict) else {"code": "HTTP_ERROR", "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": detail.get("code", "HTTP_ERROR"), "message": detail.get("message", "Request failed"), "request_id": request_id}})


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "Unexpected demo service error", "request_id": request_id}})


for router in [
    health.router,
    auth.router,
    products.router,
    inventory.router,
    pricing.router,
    coupons.router,
    cart.router,
    checkout.router,
    orders.router,
    partners.router,
    metrics_router.router,
    agent.router,
    rag.router,
    security_demo.router,
    testing.router,
]:
    app.include_router(router)
