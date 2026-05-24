from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Agentic Commerce Platform"
    app_env: str = os.getenv("APP_ENV", "local")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./agentic_commerce.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "demo-only-change-me")
    partner_api_key: str = os.getenv("PARTNER_API_KEY", "demo_partner_key")
    default_user_id: str = os.getenv("DEFAULT_USER_ID", "demo_customer_001")
    default_store_id: str = os.getenv("DEFAULT_STORE_ID", "store_1001")
    llm_mode: str = os.getenv("LLM_MODE", "mock")


settings = Settings()
