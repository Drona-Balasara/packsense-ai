"""
PackSense AI – FastAPI application entry point.

Startup sequence:
  1. Configure logging
  2. Create database tables (DDL)
  3. Seed database with fixture data (idempotent)
  4. Mount API routers

All business logic lives in engines/ and services/ — this file is
intentionally thin.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.connection import AsyncSessionLocal, create_all_tables
from app.database.seed import run_seed
from app.utils.logging import configure_logging

# ── Import routers ────────────────────────────────────────────────────────────
from app.api.foods import router as foods_router
from app.api.candidates import router as candidates_router
from app.api.analysis import router as analysis_router
from app.api.recommendations import router as recommendations_router

settings = get_settings()
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    configure_logging(debug=settings.app_debug)
    logger.info("PackSense AI %s starting up…", settings.app_version)

    # Create tables then seed
    await create_all_tables()
    logger.info("Database tables ready.")

    async with AsyncSessionLocal() as db:
        summary = await run_seed(db)
    logger.info("Seed summary: %s", summary)

    logger.info(
        "PackSense AI ready — listening on %s:%s",
        settings.app_host,
        settings.app_port,
    )
    yield

    logger.info("PackSense AI shutting down.")


# ── Application factory ────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="PackSense AI",
        description=(
            "AI-Based Intelligent Food Packaging Material Recommendation System. "
            "SIH 2026 – Problem Statement SIH26236. "
            "Ministry of Food Processing Industries. "
            "Team eX0n_ | Team ID 1305-2026 TIGC."
        ),
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(foods_router, prefix="/api", tags=["Foods"])
    app.include_router(candidates_router, prefix="/api", tags=["Candidates"])
    app.include_router(analysis_router, prefix="/api", tags=["Analysis"])
    app.include_router(recommendations_router, prefix="/api", tags=["Recommendations"])

    # ── Root health ───────────────────────────────────────────────────────────
    @app.get("/api/health", tags=["System"])
    async def health() -> dict[str, Any]:
        return {
            "status": "healthy",
            "service": "PackSense AI",
            "version": settings.app_version,
            "environment": settings.app_env,
            "prototype_disclaimer": (
                "This is a prototype system. "
                "Scientific values marked PROTOTYPE_ASSUMPTION require "
                "experimental validation before use in production decisions."
            ),
        }

    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "PackSense AI API — see /api/docs for documentation."}

    return app


app = create_app()
