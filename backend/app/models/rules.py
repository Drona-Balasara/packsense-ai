"""
PackagingRule – deterministic domain rule used by the Requirement Engine.

Rules encode knowledge such as:
  "IF oxidation risk is HIGH THEN OTR requirement is LOW"
  "IF respiration class is HIGH THEN gas exchange is REQUIRED"

Thresholds in rules must reference a source; prototype-level rules use
data_status = PROTOTYPE_ASSUMPTION.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy import String, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RuleOperator(str, Enum):
    EQUALS = "eq"
    NOT_EQUALS = "neq"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    IN = "in"
    NOT_IN = "not_in"


class RuleOutcome(str, Enum):
    """The qualitative requirement level that results from this rule."""
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"


class PackagingRule(Base):
    """
    A deterministic packaging requirement rule.

    field_path:  dot-path into FoodProfile / StorageConditions
                 e.g. "oxygen_sensitivity" or "respiration_class"
    operator:    comparison operator (eq, neq, gt, lt, in, not_in)
    value:       the value to compare against (stored as JSON for flexibility)
    required_property: the packaging property this rule constrains
                 e.g. "OTR", "WVTR", "sealability", "gas_exchange"
    outcome:     the required level of that property
    priority:    lower number = evaluated first; used when rules conflict
    """

    __tablename__ = "packaging_rules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False)

    # ── Condition ─────────────────────────────────────────────────────────────
    field_path: Mapped[str] = mapped_column(String(128), nullable=False)
    operator: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[object] = mapped_column(JSON, nullable=False)

    # ── Outcome ───────────────────────────────────────────────────────────────
    required_property: Mapped[str] = mapped_column(String(64), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)

    # ── Meta ──────────────────────────────────────────────────────────────────
    priority: Mapped[int] = mapped_column(Integer, default=100)
    source_id: Mapped[str | None] = mapped_column(String(64))
    data_status: Mapped[str] = mapped_column(
        String(64), default="PROTOTYPE_ASSUMPTION"
    )
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return (
            f"<Rule {self.id}: {self.field_path} {self.operator} {self.value}"
            f" → {self.required_property}={self.outcome}>"
        )
