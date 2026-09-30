"""
Material and MaterialProperty models.

A Material is a base packaging substrate (e.g. PET, BOPP, PE, Aluminium foil).
MaterialProperty records individual measured/reported performance values with
full provenance — critically including data_status to distinguish real evidence
from prototype assumptions.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MaterialType(str, Enum):
    FILM = "film"
    LAMINATE = "laminate"
    RIGID = "rigid"
    PAPER = "paper"
    FOIL = "foil"
    COATING = "coating"
    OTHER = "other"


class DataStatus(str, Enum):
    """
    Tracks the epistemic status of every scientific value.
    The UI MUST display this to the user — it distinguishes validated
    evidence from prototype placeholders.
    """
    VALIDATED = "VALIDATED"
    SOURCE_REQUIRED = "SOURCE_REQUIRED"
    PROTOTYPE_ASSUMPTION = "PROTOTYPE_ASSUMPTION"
    NEEDS_VALIDATION = "NEEDS_VALIDATION"


class FoodContactStatus(str, Enum):
    COMPLIANT = "compliant"           # documented compliance with a named standard
    REVIEW_REQUIRED = "review_required"  # not yet verified for this specific use
    NOT_SUITABLE = "not_suitable"
    UNKNOWN = "unknown"


class Material(Base):
    """A single packaging substrate / base material."""

    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(
        String(64), default=MaterialType.FILM.value
    )

    # ── Food contact ──────────────────────────────────────────────────────────
    # NEVER hard-code "approved" — always REVIEW_REQUIRED or referenced standard.
    # default= applies at INSERT time; we also set it in __init__ for Python-only construction.
    food_contact_status: Mapped[str] = mapped_column(
        String(64), default=FoodContactStatus.REVIEW_REQUIRED.value
    )
    food_contact_standard: Mapped[str | None] = mapped_column(String(256))

    # ── Sustainability indicators (qualitative) ───────────────────────────────
    recyclability: Mapped[str | None] = mapped_column(String(128))
    biodegradability: Mapped[str | None] = mapped_column(String(128))

    # ── Cost (range, not fake precision) ─────────────────────────────────────
    estimated_cost_inr_low: Mapped[float | None] = mapped_column(Float)
    estimated_cost_inr_high: Mapped[float | None] = mapped_column(Float)
    cost_unit: Mapped[str | None] = mapped_column(String(64))  # e.g. "per kg"

    # ── Provenance ────────────────────────────────────────────────────────────
    source_id: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)

    properties: Mapped[list["MaterialProperty"]] = relationship(
        back_populates="material", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        # Ensure Python-level defaults for columns that have INSERT defaults
        kwargs.setdefault("food_contact_status", FoodContactStatus.REVIEW_REQUIRED.value)
        kwargs.setdefault("type", MaterialType.FILM.value)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Material {self.id}: {self.name}>"


class MaterialProperty(Base):
    """
    A single measured / reported property value for a material.

    The combination of (material_id, property, temperature, humidity, thickness)
    should be unique in a production system, but is left non-unique here so that
    multiple sources can report the same property for comparison.
    """

    __tablename__ = "material_properties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("materials.id"), nullable=False
    )
    property: Mapped[str] = mapped_column(String(64), nullable=False)
    # value is nullable — if None, data_status should be NEEDS_VALIDATION
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(64))
    temperature: Mapped[float | None] = mapped_column(Float)     # °C
    humidity: Mapped[float | None] = mapped_column(Float)         # %RH
    thickness: Mapped[float | None] = mapped_column(Float)        # µm
    test_method: Mapped[str | None] = mapped_column(String(256))
    source_id: Mapped[str | None] = mapped_column(String(64))
    data_status: Mapped[str] = mapped_column(
        String(64), default=DataStatus.PROTOTYPE_ASSUMPTION.value
    )
    notes: Mapped[str | None] = mapped_column(Text)

    material: Mapped["Material"] = relationship(back_populates="properties")

    def __init__(self, **kwargs):
        kwargs.setdefault("data_status", DataStatus.PROTOTYPE_ASSUMPTION.value)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return (
            f"<MaterialProperty {self.material_id}.{self.property}="
            f"{self.value} {self.unit} [{self.data_status}]>"
        )
