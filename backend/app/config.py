"""
PackSense AI – Application Configuration
Reads settings from environment variables (with sensible defaults for dev).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "PackSense AI"
    app_version: str = "0.1.0-prototype"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ── Database ──────────────────────────────────────────────────────────────
    # SQLite for local dev; swap to PostgreSQL URI in .env for production.
    database_url: str = "sqlite+aiosqlite:///./packsense.db"

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ── Data paths ────────────────────────────────────────────────────────────
    @property
    def data_dir(self) -> Path:
        return Path(__file__).parent / "data"

    # ── Optional LLM (disabled by default) ───────────────────────────────────
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_provider and self.llm_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton for the process)."""
    return Settings()
