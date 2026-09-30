"""
Pydantic schemas for Food-related API responses.
These are the serialisation layer; they do NOT replace the ORM models.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict


class FoodSchema(BaseModel):
    """Public representation of a food commodity."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    moisture: str
    fat: str
    pH: Optional[float] = None
    water_activity: Optional[float] = None
    respiration_class: str
    oxygen_sensitivity: str
    moisture_sensitivity: str
    light_sensitivity: str
    microbial_sensitivity: str
    source_id: Optional[str] = None
    notes: Optional[str] = None


class FoodListResponse(BaseModel):
    """Paginated list of foods."""

    total: int
    items: list[FoodSchema]
