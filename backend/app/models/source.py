"""
Source – bibliographic / data-provenance record.

Every scientific value in PackSense must reference a source so that the
evidence quality can be evaluated and the chain of reasoning is auditable.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EvidenceQuality(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEEDS_VALIDATION = "NEEDS_VALIDATION"


class SourceType(str, Enum):
    PEER_REVIEWED = "peer_reviewed"
    STANDARD = "standard"
    INDUSTRY_REPORT = "industry_report"
    TEXTBOOK = "textbook"
    PROTOTYPE_ASSUMPTION = "prototype_assumption"
    REGULATORY_DOCUMENT = "regulatory_document"


class Source(Base):
    """Bibliographic record for a data source."""

    __tablename__ = "sources"

    source_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(256))
    year: Mapped[int | None] = mapped_column()
    url: Mapped[str | None] = mapped_column(String(1024))
    source_type: Mapped[str] = mapped_column(
        String(64),
        default=SourceType.PROTOTYPE_ASSUMPTION.value,
    )
    version: Mapped[str | None] = mapped_column(String(64))
    last_verified: Mapped[str | None] = mapped_column(String(32))
    evidence_quality: Mapped[str] = mapped_column(
        String(32),
        default=EvidenceQuality.NEEDS_VALIDATION.value,
    )
    notes: Mapped[str | None] = mapped_column(Text)

    def __init__(self, **kwargs):
        kwargs.setdefault("evidence_quality", EvidenceQuality.NEEDS_VALIDATION.value)
        kwargs.setdefault("source_type", SourceType.PROTOTYPE_ASSUMPTION.value)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Source {self.source_id}: {self.title[:50]}>"
