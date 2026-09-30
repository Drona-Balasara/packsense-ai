"""Repository for PackagingRule entity queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rules import PackagingRule


class RulesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> list[PackagingRule]:
        """Return all rules ordered by priority (lowest number = first evaluated)."""
        result = await self.db.execute(
            select(PackagingRule).order_by(PackagingRule.priority)
        )
        return list(result.scalars().all())

    async def get_by_property(self, required_property: str) -> list[PackagingRule]:
        result = await self.db.execute(
            select(PackagingRule)
            .where(PackagingRule.required_property == required_property)
            .order_by(PackagingRule.priority)
        )
        return list(result.scalars().all())

    async def get_by_field(self, field_path: str) -> list[PackagingRule]:
        result = await self.db.execute(
            select(PackagingRule)
            .where(PackagingRule.field_path == field_path)
            .order_by(PackagingRule.priority)
        )
        return list(result.scalars().all())
