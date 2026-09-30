"""
Candidates API router — materials and packaging structures.

Endpoints:
  GET /api/materials                        – list all base materials
  GET /api/materials/{material_id}          – get single material with properties
  GET /api/packaging-structures             – list all packaging structures
  GET /api/packaging-structures/{struct_id} – get single packaging structure
  GET /api/sources/{source_id}              – get a data source / evidence record
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.database.repositories.material_repo import MaterialRepository
from app.database.repositories.packaging_repo import PackagingRepository
from app.database.repositories.source_repo import SourceRepository

logger = logging.getLogger(__name__)
router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_session)]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _material_to_dict(material: Any) -> dict:
    """Serialise a Material ORM object (with its properties) to a plain dict."""
    props = [
        {
            "id": p.id,
            "property": p.property,
            "value": p.value,
            "unit": p.unit,
            "temperature_c": p.temperature,
            "humidity_pct": p.humidity,
            "thickness_um": p.thickness,
            "test_method": p.test_method,
            "source_id": p.source_id,
            "data_status": p.data_status,
            "notes": p.notes,
        }
        for p in (material.properties or [])
    ]
    return {
        "id": material.id,
        "name": material.name,
        "type": material.type,
        "food_contact_status": material.food_contact_status,
        "food_contact_standard": material.food_contact_standard,
        "recyclability": material.recyclability,
        "biodegradability": material.biodegradability,
        "estimated_cost_inr_low": material.estimated_cost_inr_low,
        "estimated_cost_inr_high": material.estimated_cost_inr_high,
        "cost_unit": material.cost_unit,
        "source_id": material.source_id,
        "notes": material.notes,
        "properties": props,
    }


def _structure_to_dict(s: Any) -> dict:
    """Serialise a PackagingStructure ORM object to a plain dict."""
    return {
        "id": s.id,
        "name": s.name,
        "layers": s.layers,
        "sealant": s.sealant,
        "structure_type": s.structure_type,
        "material_ids": s.material_ids,
        "food_contact_status": s.food_contact_status,
        "food_contact_standard": s.food_contact_standard,
        "estimated_cost_inr_low": s.estimated_cost_inr_low,
        "estimated_cost_inr_high": s.estimated_cost_inr_high,
        "cost_unit": s.cost_unit,
        "sustainability_indicators": s.sustainability_indicators,
        "source_id": s.source_id,
        "notes": s.notes,
    }


def _source_to_dict(src: Any) -> dict:
    return {
        "source_id": src.source_id,
        "title": src.title,
        "publisher": src.publisher,
        "year": src.year,
        "url": src.url,
        "source_type": src.source_type,
        "version": src.version,
        "last_verified": src.last_verified,
        "evidence_quality": src.evidence_quality,
        "notes": src.notes,
    }


# ── Materials ──────────────────────────────────────────────────────────────────

@router.get(
    "/materials",
    summary="List all packaging base materials",
    description=(
        "Returns all base materials in the knowledge base with their known properties. "
        "Property values marked NEEDS_VALIDATION require experimental confirmation "
        "before use in production decisions."
    ),
)
async def list_materials(db: DBSession) -> dict:
    repo = MaterialRepository(db)
    materials = await repo.get_all()
    return {
        "total": len(materials),
        "items": [_material_to_dict(m) for m in materials],
    }


@router.get(
    "/materials/{material_id}",
    summary="Get a base material by ID",
    responses={404: {"description": "Material not found"}},
)
async def get_material(material_id: str, db: DBSession) -> dict:
    repo = MaterialRepository(db)
    material = await repo.get_by_id(material_id)
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found.",
        )
    return _material_to_dict(material)


# ── Packaging structures ───────────────────────────────────────────────────────

@router.get(
    "/packaging-structures",
    summary="List all packaging structures",
    description=(
        "Returns all packaging structures available for evaluation. "
        "Structures are multi-layer formats (e.g. PET/MetPET/PE). "
        "Regulatory status is REVIEW for all prototype structures — "
        "compliance verification is required before production use."
    ),
)
async def list_packaging_structures(db: DBSession) -> dict:
    repo = PackagingRepository(db)
    structures = await repo.get_all()
    return {
        "total": len(structures),
        "items": [_structure_to_dict(s) for s in structures],
    }


@router.get(
    "/packaging-structures/{structure_id}",
    summary="Get a packaging structure by ID",
    responses={404: {"description": "Packaging structure not found"}},
)
async def get_packaging_structure(structure_id: str, db: DBSession) -> dict:
    repo = PackagingRepository(db)
    structure = await repo.get_by_id(structure_id)
    if structure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Packaging structure '{structure_id}' not found.",
        )
    return _structure_to_dict(structure)


# ── Sources / Evidence ─────────────────────────────────────────────────────────

@router.get(
    "/sources",
    summary="List all data sources",
    description=(
        "Returns all bibliographic sources used in the PackSense knowledge base. "
        "Every scientific value should be traceable to a source record."
    ),
)
async def list_sources(db: DBSession) -> dict:
    repo = SourceRepository(db)
    sources = await repo.get_all()
    return {
        "total": len(sources),
        "items": [_source_to_dict(s) for s in sources],
    }


@router.get(
    "/sources/{source_id}",
    summary="Get a data source / evidence record by ID",
    responses={404: {"description": "Source not found"}},
)
async def get_source(source_id: str, db: DBSession) -> dict:
    repo = SourceRepository(db)
    source = await repo.get_by_id(source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found.",
        )
    return _source_to_dict(source)
