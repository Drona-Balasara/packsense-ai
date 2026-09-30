"""
Pydantic schemas for the /analyze and /recommend request/response cycle.
These schemas define the public API contract for the decision-support pipeline.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ── Request bodies ─────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Input for POST /api/analyze — produces risk profile + requirements."""

    food_id: str = Field(..., description="ID of the food commodity (e.g. FOOD001)")
    temperature: float = Field(
        ..., ge=-30, le=60, description="Storage temperature in °C"
    )
    relative_humidity: float = Field(
        ..., ge=0, le=100, description="Relative humidity in %"
    )
    target_shelf_life_days: int = Field(
        ..., ge=1, le=3650,
        description=(
            "Target shelf life in days — this is a DESIGN REQUIREMENT, "
            "not a system prediction."
        ),
    )


class RankingWeights(BaseModel):
    """Configurable TOPSIS criteria weights. Must sum to 1.0 (±0.01 tolerance)."""

    technical_fit: float = Field(0.40, ge=0.0, le=1.0)
    cost: float = Field(0.20, ge=0.0, le=1.0)
    sustainability: float = Field(0.20, ge=0.0, le=1.0)
    evidence_quality: float = Field(0.20, ge=0.0, le=1.0)

    @field_validator("evidence_quality")
    @classmethod
    def weights_sum_to_one(cls, v: float, info: Any) -> float:
        vals = info.data
        total = vals.get("technical_fit", 0) + vals.get("cost", 0) + vals.get("sustainability", 0) + v
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Ranking weights must sum to 1.0 (got {total:.4f}). "
                "These are prototype configuration values."
            )
        return v


class RecommendRequest(AnalyzeRequest):
    """Input for POST /api/recommend — full decision pipeline."""

    ranking_weights: RankingWeights = Field(
        default_factory=RankingWeights,
        description="TOPSIS criteria weights (configurable prototype defaults)",
    )


# ── Intermediate response pieces ───────────────────────────────────────────────

class RiskEntry(BaseModel):
    """A single risk dimension with its level and reasoning."""
    risk: str
    level: str          # NONE / LOW / MEDIUM / HIGH
    reasoning: str
    data_status: str = "PROTOTYPE_ASSUMPTION"


class RiskProfileSchema(BaseModel):
    food_id: str
    food_name: str
    risks: list[RiskEntry]


class RequirementEntry(BaseModel):
    """A derived packaging property requirement."""
    property: str       # e.g. OTR, WVTR, sealability
    requirement: str    # e.g. LOW, HIGH, REQUIRED
    reason: str
    data_status: str = "PROTOTYPE_ASSUMPTION"


class RequirementsSchema(BaseModel):
    food_id: str
    requirements: list[RequirementEntry]


class AnalyzeResponse(BaseModel):
    """Response body for POST /api/analyze."""
    analysis_id: str
    input: AnalyzeRequest
    food_profile: dict[str, Any]
    risk_profile: RiskProfileSchema
    requirements: RequirementsSchema
    validation_notes: list[str] = Field(default_factory=list)
