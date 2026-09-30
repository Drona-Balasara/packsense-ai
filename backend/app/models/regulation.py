"""
Regulation – regulatory compliance records for packaging materials.

CRITICAL: This model stores what is KNOWN about regulatory status from
published standards. It does NOT confer legal approval. The system uses
these records to flag materials that REQUIRE regulatory verification before
use — never to claim they are "FSSAI Approved" in a generic sense.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RegStatus(str, Enum):
    """
    Regulatory screening outcome for a material in a given jurisdiction.
    
    LISTED   – the material appears in the referenced standard; full
               compliance for a specific application still requires
               verification against conditions of use.
    REVIEW   – available information is insufficient for a determination;
               professional verification required.
    NOT_LISTED – material does not appear in the referenced standard for
                food contact; not suitable without further justification.
    """
    LISTED = "LISTED"
    REVIEW = "REVIEW"
    NOT_LISTED = "NOT_LISTED"


class Regulation(Base):
    """Regulatory record linking a material to a published standard."""

    __tablename__ = "regulations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    material_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # ── Standard reference ────────────────────────────────────────────────────
    standard: Mapped[str] = mapped_column(String(256), nullable=False)
    jurisdiction: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(
        String(32), default=RegStatus.REVIEW.value
    )

    # ── Detail ────────────────────────────────────────────────────────────────
    # JSON object of conditions/requirements if known (e.g. migration limits)
    requirements: Mapped[dict | None] = mapped_column(JSON)
    conditions_of_use: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    # ── Provenance ────────────────────────────────────────────────────────────
    source: Mapped[str | None] = mapped_column(String(512))
    version: Mapped[str | None] = mapped_column(String(64))
    effective_date: Mapped[str | None] = mapped_column(String(32))
    last_verified: Mapped[str | None] = mapped_column(String(32))

    def __repr__(self) -> str:
        return (
            f"<Regulation {self.id}: {self.material_id} "
            f"{self.standard} [{self.status}]>"
        )
