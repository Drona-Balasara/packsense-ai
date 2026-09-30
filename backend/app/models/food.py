"""
Food – the commodity being analysed.

Qualitative/categorical attributes are stored as string enums so that the
risk engine can apply rules deterministically without invented numeric thresholds.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SensitivityLevel(str, Enum):
    """Generic three-level sensitivity scale."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RespirationClass(str, Enum):
    """Biological respiration classification for produce and non-produce."""
    NONE = "NONE"           # processed / snack foods
    LOW = "LOW"             # low-respiration produce
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"           # leafy greens, cut produce, etc.
    CLIMACTERIC = "CLIMACTERIC"  # fruit that ripens post-harvest


class FoodCategory(str, Enum):
    SNACK = "snack"
    FRESH_PRODUCE = "fresh_produce"
    PROCESSED = "processed"
    DAIRY = "dairy"
    BEVERAGE = "beverage"
    GRAIN = "grain"
    MEAT = "meat"
    OTHER = "other"


class Food(Base):
    """A food commodity entry in the knowledge base."""

    __tablename__ = "foods"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)

    # ── Compositional / physicochemical attributes (qualitative) ─────────────
    moisture: Mapped[str] = mapped_column(
        String(32), default=SensitivityLevel.MEDIUM.value
    )
    fat: Mapped[str] = mapped_column(
        String(32), default=SensitivityLevel.LOW.value
    )
    # pH and water activity stored as floats when available; nullable means unknown.
    pH: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_activity: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Degradation sensitivity (qualitative) ────────────────────────────────
    respiration_class: Mapped[str] = mapped_column(
        String(32), default=RespirationClass.NONE.value
    )
    oxygen_sensitivity: Mapped[str] = mapped_column(
        String(32), default=SensitivityLevel.LOW.value
    )
    moisture_sensitivity: Mapped[str] = mapped_column(
        String(32), default=SensitivityLevel.LOW.value
    )
    light_sensitivity: Mapped[str] = mapped_column(
        String(32), default=SensitivityLevel.LOW.value
    )
    microbial_sensitivity: Mapped[str] = mapped_column(
        String(32), default=SensitivityLevel.LOW.value
    )

    # ── Provenance ────────────────────────────────────────────────────────────
    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Food {self.id}: {self.name}>"
