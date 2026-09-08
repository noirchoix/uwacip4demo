from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIPE4_", env_file=".env", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://pipe4:pipe4@localhost:5432/pipe4"
    redis_url: str = "redis://localhost:6379/0"
    policy_path: Path = Path("config/policies/pipe4-policy.v1.yaml")

    evidence_backend: str = "local"
    evidence_local_root: Path = Path("evidence")
    evidence_bucket: str | None = None
    evidence_endpoint_url: str | None = None
    evidence_access_key_id: str | None = None
    evidence_secret_access_key: str | None = None

    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    jwt_jwks_url: str | None = None
    jwt_hs256_secret: str | None = None
    internal_api_token: str = Field(default="change-me", min_length=8)

    ai_gateway_url: str | None = None
    ai_gateway_token: str | None = None

    enable_dev_fixtures: bool = False
    rate_limit_default_per_minute: int = 120
    rate_limit_nearby_per_minute: int = 60
    rate_limit_witness_per_minute: int = 20
    rate_limit_mutation_per_minute: int = 60
    cors_allowed_origins: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
