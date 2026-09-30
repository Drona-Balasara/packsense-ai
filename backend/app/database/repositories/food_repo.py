"""Repository for Food entity queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Food


class FoodRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, food_id: str) -> Food | None:
        return await self.db.get(Food, food_id)

    async def get_all(self) -> list[Food]:
        result = await self.db.execute(select(Food).order_by(Food.name))
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[Food]:
        result = await self.db.execute(
            select(Food).where(Food.category == category).order_by(Food.name)
        )
        return list(result.scalars().all())
