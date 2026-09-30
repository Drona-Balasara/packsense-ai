"""
Analysis API router — Phase 2+ implementation.

POST /api/analyze  →  food profile + risk vector + packaging requirements.

This stub returns HTTP 501 (Not Implemented) until the Risk Engine and
Requirement Engine are wired up in Phase 2.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.analysis import AnalyzeRequest

router = APIRouter()


@router.post(
    "/analyze",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Analyse a food commodity (Phase 2)",
    description=(
        "**Phase 2 – Not yet implemented.** "
        "Will accept food ID + storage conditions and return the food profile, "
        "risk vector, and derived packaging requirements. "
        "Implement after Risk Engine and Requirement Engine are complete."
    ),
)
async def analyze(_body: AnalyzeRequest) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "message": "POST /api/analyze is not yet implemented.",
            "phase": "Phase 2 — Risk Engine + Requirement Engine",
            "status": "pending",
        },
    )
