"""Repository for Material and MaterialProperty entity queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.material import Material, MaterialProperty


class MaterialRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, material_id: str) -> Material | None:
        result = await self.db.execute(
            select(Material)
            .where(Material.id == material_id)
            .options(selectinload(Material.properties))
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Material]:
        result = await self.db.execute(
            select(Material)
            .options(selectinload(Material.properties))
            .order_by(Material.name)
        )
        return list(result.scalars().all())

    async def get_properties(
        self, material_id: str, property_name: str | None = None
    ) -> list[MaterialProperty]:
        query = select(MaterialProperty).where(
            MaterialProperty.material_id == material_id
        )
        if property_name:
            query = query.where(MaterialProperty.property == property_name)
        result = await self.db.execute(query)
        return list(result.scalars().all())
