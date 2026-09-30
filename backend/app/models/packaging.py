"""
PackagingStructure – a complete multi-layer packaging format.

Examples: PET/PE, PET/MetPET/PE, BOPP/MetBOPP/PE, PET/AL/PE, Perforated PE.
Each structure is composed of one or more base materials (material_ids is a
JSON-serialised list of Material IDs).
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StructureType(str, Enum):
    FLEXIBLE_LAMINATE = "flexible_laminate"
    MONO_FILM = "mono_film"
    RIGID_CONTAINER = "rigid_container"
    PAPER_BASED = "paper_based"
    PERFORATED = "perforated"
    MAP_COMPATIBLE = "map_compatible"
    OTHER = "other"


class PackagingStructure(Base):
    """
    A complete packaging structure potentially suitable for food use.

    food_contact_status refers to the innermost (sealant) layer and must
    reference a standard rather than claiming generic approval.
    """

    __tablename__ = "packaging_structures"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)

    # ── Structure composition ─────────────────────────────────────────────────
    layers: Mapped[list | None] = mapped_column(JSON)    # ordered list of layer names
    sealant: Mapped[str | None] = mapped_column(String(128))
    structure_type: Mapped[str] = mapped_column(
        String(64), default=StructureType.FLEXIBLE_LAMINATE.value
    )
    material_ids: Mapped[list | None] = mapped_column(JSON)  # list of Material.id

    # ── Food contact ──────────────────────────────────────────────────────────
    food_contact_status: Mapped[str] = mapped_column(
        String(64), default="review_required"
    )
    food_contact_standard: Mapped[str | None] = mapped_column(String(256))

    # ── Cost indicator (range, not fake precision) ────────────────────────────
    estimated_cost_inr_low: Mapped[float | None] = mapped_column()
    estimated_cost_inr_high: Mapped[float | None] = mapped_column()
    cost_unit: Mapped[str | None] = mapped_column(String(64))

    # ── Sustainability indicators ─────────────────────────────────────────────
    # Stored as a JSON object of indicator → qualitative value
    sustainability_indicators: Mapped[dict | None] = mapped_column(JSON)

    # ── Provenance ────────────────────────────────────────────────────────────
    source_id: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)

    def __init__(self, **kwargs):
        kwargs.setdefault("food_contact_status", "review_required")
        kwargs.setdefault("structure_type", StructureType.FLEXIBLE_LAMINATE.value)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<PackagingStructure {self.id}: {self.name}>"
