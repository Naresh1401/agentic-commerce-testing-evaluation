# Testing Strategy

Deterministic API tests cover products, inventory, carts, checkout, orders, and error formats.

Contract tests validate OpenAPI generation and key response schemas.

Agent tests use a golden dataset because agent behavior can vary when a real LLM is enabled.

Prompt injection tests verify blocked requests such as data exfiltration and unauthorized payment.

RBAC tests verify row-level access and partner/admin boundaries.

RAG evaluation checks grounded answers, citations, and unsupported question refusal.
