"""
Database seeder — loads JSON fixture files into the database on first run.

Each entity type is loaded idempotently: if a record with the same primary key
already exists it is skipped, so re-running the seeder is safe.

Load order matters because of foreign-key relationships:
  Sources → Foods → Materials → MaterialProperties →
  PackagingStructures → Rules → Regulations
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food import Food
from app.models.material import Material, MaterialProperty
from app.models.packaging import PackagingStructure
from app.models.regulation import Regulation
from app.models.rules import PackagingRule
from app.models.source import Source

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    if not path.exists():
        logger.warning("Seed file not found: %s", path)
        return []
    with path.open(encoding="utf-8") as f:
        return json.load(f)


async def _seed_sources(db: AsyncSession) -> int:
    records = _load_json("sources.json")
    count = 0
    for rec in records:
        existing = await db.get(Source, rec["source_id"])
        if existing:
            continue
        db.add(Source(**rec))
        count += 1
    return count


async def _seed_foods(db: AsyncSession) -> int:
    records = _load_json("foods.json")
    count = 0
    for rec in records:
        existing = await db.get(Food, rec["id"])
        if existing:
            continue
        db.add(Food(**rec))
        count += 1
    return count


async def _seed_materials(db: AsyncSession) -> int:
    records = _load_json("materials.json")
    count = 0
    for rec in records:
        existing = await db.get(Material, rec["id"])
        if existing:
            continue
        db.add(Material(**rec))
        count += 1
    return count


async def _seed_material_properties(db: AsyncSession) -> int:
    records = _load_json("material_properties.json")
    count = 0
    for rec in records:
        # Check by integer primary key
        existing = await db.get(MaterialProperty, rec["id"])
        if existing:
            continue
        db.add(MaterialProperty(**rec))
        count += 1
    return count


async def _seed_packaging_structures(db: AsyncSession) -> int:
    records = _load_json("packaging_structures.json")
    count = 0
    for rec in records:
        existing = await db.get(PackagingStructure, rec["id"])
        if existing:
            continue
        db.add(PackagingStructure(**rec))
        count += 1
    return count


async def _seed_rules(db: AsyncSession) -> int:
    records = _load_json("rules.json")
    count = 0
    for rec in records:
        existing = await db.get(PackagingRule, rec["id"])
        if existing:
            continue
        db.add(PackagingRule(**rec))
        count += 1
    return count


async def _seed_regulations(db: AsyncSession) -> int:
    records = _load_json("regulations.json")
    count = 0
    for rec in records:
        existing = await db.get(Regulation, rec["id"])
        if existing:
            continue
        db.add(Regulation(**rec))
        count += 1
    return count


async def run_seed(db: AsyncSession) -> dict[str, int]:
    """
    Load all seed data into the database.
    Returns a dict of {entity: records_inserted}.
    """
    logger.info("Starting database seed...")

    sources_n = await _seed_sources(db)
    await db.flush()

    foods_n = await _seed_foods(db)
    await db.flush()

    materials_n = await _seed_materials(db)
    await db.flush()

    props_n = await _seed_material_properties(db)
    await db.flush()

    structures_n = await _seed_packaging_structures(db)
    await db.flush()

    rules_n = await _seed_rules(db)
    await db.flush()

    regulations_n = await _seed_regulations(db)
    await db.flush()

    await db.commit()

    summary = {
        "sources": sources_n,
        "foods": foods_n,
        "materials": materials_n,
        "material_properties": props_n,
        "packaging_structures": structures_n,
        "rules": rules_n,
        "regulations": regulations_n,
    }
    total = sum(summary.values())
    logger.info("Seed complete — %d records inserted: %s", total, summary)
    return summary
