"""Repository for Source entity queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source


class SourceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, source_id: str) -> Source | None:
        return await self.db.get(Source, source_id)

    async def get_all(self) -> list[Source]:
        result = await self.db.execute(
            select(Source).order_by(Source.source_id)
        )
        return list(result.scalars().all())

    async def get_by_quality(self, quality: str) -> list[Source]:
        result = await self.db.execute(
            select(Source)
            .where(Source.evidence_quality == quality)
            .order_by(Source.source_id)
        )
        return list(result.scalars().all())
