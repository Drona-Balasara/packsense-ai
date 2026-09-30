"""
Foods API router.

Endpoints:
  GET /api/foods            – list all food commodities
  GET /api/foods/{food_id}  – get a single food commodity by ID
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.database.repositories.food_repo import FoodRepository
from app.schemas.food import FoodListResponse, FoodSchema

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Type alias for injected session ───────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/foods",
    response_model=FoodListResponse,
    summary="List all food commodities",
    description=(
        "Returns all food commodities available in the PackSense knowledge base. "
        "These are the prototype seed foods (Potato Chips, Roasted Peanuts, Tomato) "
        "plus any additions. Use a food ID from this list to call /api/analyze or "
        "/api/recommend."
    ),
)
async def list_foods(db: DBSession) -> FoodListResponse:
    repo = FoodRepository(db)
    foods = await repo.get_all()
    return FoodListResponse(
        total=len(foods),
        items=[FoodSchema.model_validate(f) for f in foods],
    )


@router.get(
    "/foods/{food_id}",
    response_model=FoodSchema,
    summary="Get a food commodity by ID",
    responses={
        404: {"description": "Food commodity not found"},
    },
)
async def get_food(food_id: str, db: DBSession) -> FoodSchema:
    repo = FoodRepository(db)
    food = await repo.get_by_id(food_id)
    if food is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food commodity '{food_id}' not found. "
                   f"Use GET /api/foods to list available IDs.",
        )
    return FoodSchema.model_validate(food)
