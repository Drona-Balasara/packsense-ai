"""
Recommendations API router — Phase 5+ implementation.

POST /api/recommend                    →  full decision pipeline + ranking
GET  /api/recommendations/{analysis_id} →  retrieve a stored recommendation

Both endpoints return HTTP 501 (Not Implemented) until the full pipeline
(Phases 2–5) is wired up.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.analysis import RecommendRequest

router = APIRouter()


@router.post(
    "/recommend",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Full recommendation pipeline (Phase 5)",
    description=(
        "**Phase 5 – Not yet implemented.** "
        "Executes the complete 12-step decision pipeline: "
        "food profile → risk → requirements → candidates → regulatory filter → "
        "technical filter → MAP analysis → cost → sustainability → TOPSIS → "
        "explanation → evidence. "
        "Implement after all engines are complete (Phases 2–5)."
    ),
)
async def recommend(_body: RecommendRequest) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "message": "POST /api/recommend is not yet implemented.",
            "phase": "Phase 5 — Full pipeline + TOPSIS ranking",
            "status": "pending",
        },
    )


@router.get(
    "/recommendations/{analysis_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Retrieve a stored recommendation (Phase 6)",
    description="**Phase 6 – Not yet implemented.** Will retrieve a stored recommendation result by analysis ID.",
)
async def get_recommendation(analysis_id: str) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "message": f"GET /api/recommendations/{analysis_id} is not yet implemented.",
            "phase": "Phase 6 — Persistence + retrieval",
            "status": "pending",
        },
    )
