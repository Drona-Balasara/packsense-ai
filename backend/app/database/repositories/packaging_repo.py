"""Repository for PackagingStructure entity queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.packaging import PackagingStructure
from app.models.regulation import Regulation


class PackagingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, structure_id: str) -> PackagingStructure | None:
        return await self.db.get(PackagingStructure, structure_id)

    async def get_all(self) -> list[PackagingStructure]:
        result = await self.db.execute(
            select(PackagingStructure).order_by(PackagingStructure.name)
        )
        return list(result.scalars().all())

    async def get_by_type(self, structure_type: str) -> list[PackagingStructure]:
        result = await self.db.execute(
            select(PackagingStructure)
            .where(PackagingStructure.structure_type == structure_type)
            .order_by(PackagingStructure.name)
        )
        return list(result.scalars().all())

    async def get_regulations_for_material(
        self, material_id: str
    ) -> list[Regulation]:
        result = await self.db.execute(
            select(Regulation).where(Regulation.material_id == material_id)
        )
        return list(result.scalars().all())
