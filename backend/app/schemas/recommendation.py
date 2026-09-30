"""
Pydantic schemas for the final recommendation response.

The response is structured to support complete traceability:
  Input → Risk Profile → Requirements → Candidate Evaluation → Ranking → Evidence
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class SustainabilityIndicators(BaseModel):
    recyclability: Optional[str] = None
    biodegradability: Optional[str] = None
    layer_count: Optional[int] = None
    material_complexity: Optional[str] = None
    data_status: str = "PROTOTYPE_ASSUMPTION"


class EvidenceRef(BaseModel):
    """A traceable evidence reference attached to a value or decision."""
    source_id: str
    title: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    evidence_quality: str  # HIGH / MEDIUM / LOW / NEEDS_VALIDATION
    data_status: str = "PROTOTYPE_ASSUMPTION"


class CandidateEvaluation(BaseModel):
    """Per-candidate result from the filtering pipeline."""
    candidate_id: str
    candidate_name: str
    regulatory_status: str      # LISTED / REVIEW / NOT_LISTED
    regulatory_reason: Optional[str] = None
    technical_status: str       # PASS / FAIL / REVIEW
    failed_requirements: list[dict[str, str]] = Field(default_factory=list)
    cost_indicator: Optional[str] = None   # LOW / MEDIUM / HIGH / UNAVAILABLE
    sustainability: SustainabilityIndicators = Field(
        default_factory=SustainabilityIndicators
    )
    evidence_quality: str = "NEEDS_VALIDATION"


class RankedCandidate(BaseModel):
    """A packaging structure that survived all hard constraints, with rank."""
    rank: int
    candidate_id: str
    candidate_name: str
    topsis_score: Optional[float] = None
    technical_fit: str          # HIGH / MEDIUM / LOW
    cost_indicator: str         # LOW / MEDIUM / HIGH / UNAVAILABLE
    sustainability: SustainabilityIndicators
    evidence_quality: str
    reasons: list[str]          # human-readable explanation steps
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class RejectedCandidate(BaseModel):
    """A candidate removed during regulatory or technical filtering."""
    candidate_id: str
    candidate_name: str
    rejection_stage: str        # REGULATORY / TECHNICAL
    reason: str
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """Complete response from POST /api/recommend."""
    analysis_id: str
    input: dict[str, Any]
    food_profile: dict[str, Any]
    risk_profile: dict[str, Any]
    requirements: list[dict[str, Any]]
    candidates_evaluated: list[CandidateEvaluation]
    feasible_candidates: list[str]     # list of candidate IDs
    ranked_candidates: list[RankedCandidate]
    alternatives: list[RankedCandidate] = Field(default_factory=list)
    rejected_candidates: list[RejectedCandidate] = Field(default_factory=list)
    map_analysis: Optional[dict[str, Any]] = None
    validation_notes: list[str] = Field(default_factory=list)
    sources: list[EvidenceRef] = Field(default_factory=list)
    prototype_disclaimer: str = (
        "This output is produced by a prototype system. "
        "All scientific values marked PROTOTYPE_ASSUMPTION require "
        "experimental validation before use in production decisions. "
        "Regulatory screening does not constitute legal approval."
    )
