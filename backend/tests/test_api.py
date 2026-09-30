"""
Phase 1 API tests.

Covers:
  - GET /api/health
  - GET /api/foods
  - GET /api/foods/{food_id}   (valid + invalid)
  - GET /api/materials
  - GET /api/materials/{material_id}
  - GET /api/packaging-structures
  - GET /api/packaging-structures/{structure_id}
  - GET /api/sources
  - GET /api/sources/{source_id}
  - POST /api/analyze          (501 stub)
  - POST /api/recommend        (501 stub)
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


# ── Health ─────────────────────────────────────────────────────────────────────

class TestHealth:
    async def test_health_returns_200(self, client: AsyncClient):
        response = await client.get("/api/health")
        assert response.status_code == 200

    async def test_health_body(self, client: AsyncClient):
        data = (await client.get("/api/health")).json()
        assert data["status"] == "healthy"
        assert data["service"] == "PackSense AI"
        assert "version" in data
        assert "prototype_disclaimer" in data

    async def test_health_is_deterministic(self, client: AsyncClient):
        """Calling health twice should return the same status."""
        r1 = (await client.get("/api/health")).json()
        r2 = (await client.get("/api/health")).json()
        assert r1["status"] == r2["status"]


# ── Foods ──────────────────────────────────────────────────────────────────────

class TestFoods:
    async def test_list_foods_returns_200(self, client: AsyncClient):
        response = await client.get("/api/foods")
        assert response.status_code == 200

    async def test_list_foods_has_items(self, client: AsyncClient):
        data = (await client.get("/api/foods")).json()
        assert "items" in data
        assert data["total"] >= 3, "Seed data must contain at least 3 foods"

    async def test_list_foods_contains_prototype_cases(self, client: AsyncClient):
        data = (await client.get("/api/foods")).json()
        names = {item["name"] for item in data["items"]}
        assert "Potato Chips" in names
        assert "Roasted Peanuts" in names
        assert "Tomato" in names

    async def test_get_food_potato_chips(self, client: AsyncClient):
        response = await client.get("/api/foods/FOOD001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "FOOD001"
        assert data["name"] == "Potato Chips"
        assert data["category"] == "snack"

    async def test_get_food_roasted_peanuts(self, client: AsyncClient):
        response = await client.get("/api/foods/FOOD002")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "FOOD002"
        assert data["name"] == "Roasted Peanuts"

    async def test_get_food_tomato(self, client: AsyncClient):
        response = await client.get("/api/foods/FOOD003")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "FOOD003"
        assert data["name"] == "Tomato"
        assert data["category"] == "fresh_produce"

    async def test_get_food_not_found(self, client: AsyncClient):
        response = await client.get("/api/foods/FOOD_DOES_NOT_EXIST")
        assert response.status_code == 404

    async def test_food_has_sensitivity_fields(self, client: AsyncClient):
        data = (await client.get("/api/foods/FOOD001")).json()
        for field in ("oxygen_sensitivity", "moisture_sensitivity",
                      "respiration_class", "light_sensitivity",
                      "microbial_sensitivity"):
            assert field in data, f"Missing field: {field}"

    async def test_potato_chips_high_oxidation_sensitivity(self, client: AsyncClient):
        """Potato Chips must be marked HIGH oxygen sensitivity (drives requirement engine)."""
        data = (await client.get("/api/foods/FOOD001")).json()
        assert data["oxygen_sensitivity"] == "HIGH"

    async def test_potato_chips_high_moisture_sensitivity(self, client: AsyncClient):
        data = (await client.get("/api/foods/FOOD001")).json()
        assert data["moisture_sensitivity"] == "HIGH"

    async def test_tomato_climacteric_respiration(self, client: AsyncClient):
        """Tomato must be marked CLIMACTERIC — drives MAP engine path."""
        data = (await client.get("/api/foods/FOOD003")).json()
        assert data["respiration_class"] == "CLIMACTERIC"

    async def test_tomato_no_invented_numeric_values(self, client: AsyncClient):
        """pH and water_activity should be null for prototype seed data."""
        data = (await client.get("/api/foods/FOOD003")).json()
        # These are nullable — prototype does not fabricate numeric values
        assert data.get("pH") is None
        assert data.get("water_activity") is None


# ── Materials ──────────────────────────────────────────────────────────────────

class TestMaterials:
    async def test_list_materials_returns_200(self, client: AsyncClient):
        response = await client.get("/api/materials")
        assert response.status_code == 200

    async def test_list_materials_has_items(self, client: AsyncClient):
        data = (await client.get("/api/materials")).json()
        assert data["total"] >= 8

    async def test_get_material_pet(self, client: AsyncClient):
        response = await client.get("/api/materials/MAT001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "MAT001"

    async def test_get_material_not_found(self, client: AsyncClient):
        response = await client.get("/api/materials/MAT_DOES_NOT_EXIST")
        assert response.status_code == 404

    async def test_material_food_contact_status_is_not_approved(
        self, client: AsyncClient
    ):
        """
        CRITICAL: No material should claim unconditional food-contact approval.
        All prototype materials must be 'review_required'.
        """
        data = (await client.get("/api/materials")).json()
        for item in data["items"]:
            assert item["food_contact_status"] != "compliant", (
                f"Material {item['id']} claims 'compliant' food contact status — "
                "this is not permitted in prototype without a specific validated standard reference."
            )

    async def test_material_properties_have_data_status(self, client: AsyncClient):
        """Every material property must carry a data_status field."""
        data = (await client.get("/api/materials/MAT001")).json()
        for prop in data.get("properties", []):
            assert "data_status" in prop, f"Property missing data_status: {prop}"

    async def test_material_property_values_are_null_for_prototype(
        self, client: AsyncClient
    ):
        """
        Prototype material property values must be null (NEEDS_VALIDATION).
        No fabricated OTR/WVTR numbers should appear.
        """
        data = (await client.get("/api/materials")).json()
        for item in data["items"]:
            for prop in item.get("properties", []):
                if prop["data_status"] in ("NEEDS_VALIDATION", "PROTOTYPE_ASSUMPTION"):
                    # value must not be a fabricated specific number
                    # (null is the correct representation)
                    assert prop["value"] is None, (
                        f"Material {item['id']} property {prop['property']} has "
                        f"data_status={prop['data_status']} but value={prop['value']} "
                        "(should be null — do not fabricate scientific values)."
                    )


# ── Packaging Structures ───────────────────────────────────────────────────────

class TestPackagingStructures:
    async def test_list_structures_returns_200(self, client: AsyncClient):
        response = await client.get("/api/packaging-structures")
        assert response.status_code == 200

    async def test_list_structures_has_items(self, client: AsyncClient):
        data = (await client.get("/api/packaging-structures")).json()
        assert data["total"] >= 8

    async def test_get_structure_pet_al_pe(self, client: AsyncClient):
        response = await client.get("/api/packaging-structures/PKG005")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PKG005"
        assert "PET" in data["name"]

    async def test_get_structure_not_found(self, client: AsyncClient):
        response = await client.get("/api/packaging-structures/PKG_NONE")
        assert response.status_code == 404

    async def test_structures_have_layers(self, client: AsyncClient):
        data = (await client.get("/api/packaging-structures")).json()
        for item in data["items"]:
            assert item.get("layers") is not None, (
                f"Structure {item['id']} missing layers"
            )

    async def test_structures_have_sustainability_indicators(
        self, client: AsyncClient
    ):
        data = (await client.get("/api/packaging-structures")).json()
        for item in data["items"]:
            si = item.get("sustainability_indicators")
            assert si is not None, f"Structure {item['id']} missing sustainability_indicators"
            assert "data_status" in si, (
                f"Structure {item['id']} sustainability_indicators missing data_status"
            )

    async def test_perforated_structures_present(self, client: AsyncClient):
        """MAP-relevant perforated structures must exist for fresh produce analysis."""
        data = (await client.get("/api/packaging-structures")).json()
        structure_types = {item["structure_type"] for item in data["items"]}
        assert "perforated" in structure_types, (
            "No perforated structures found — required for tomato/fresh produce MAP analysis"
        )


# ── Sources ────────────────────────────────────────────────────────────────────

class TestSources:
    async def test_list_sources_returns_200(self, client: AsyncClient):
        response = await client.get("/api/sources")
        assert response.status_code == 200

    async def test_list_sources_has_items(self, client: AsyncClient):
        data = (await client.get("/api/sources")).json()
        assert data["total"] >= 6

    async def test_get_source_by_id(self, client: AsyncClient):
        response = await client.get("/api/sources/SRC-PROTO-001")
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "SRC-PROTO-001"

    async def test_get_source_not_found(self, client: AsyncClient):
        response = await client.get("/api/sources/SRC_DOES_NOT_EXIST")
        assert response.status_code == 404

    async def test_sources_have_evidence_quality(self, client: AsyncClient):
        data = (await client.get("/api/sources")).json()
        for src in data["items"]:
            assert "evidence_quality" in src, f"Source {src['source_id']} missing evidence_quality"


# ── Phase stubs ────────────────────────────────────────────────────────────────

class TestPhaseStubs:
    """
    Verify that Phase 2+ endpoints return HTTP 501 (Not Implemented)
    rather than 200 with fabricated data.
    """

    async def test_analyze_returns_501(self, client: AsyncClient):
        payload = {
            "food_id": "FOOD001",
            "temperature": 30,
            "relative_humidity": 65,
            "target_shelf_life_days": 180,
        }
        response = await client.post("/api/analyze", json=payload)
        assert response.status_code == 501, (
            "POST /api/analyze must return 501 until Phase 2 is implemented — "
            "it must NOT return fabricated recommendation data."
        )

    async def test_recommend_returns_501(self, client: AsyncClient):
        payload = {
            "food_id": "FOOD001",
            "temperature": 30,
            "relative_humidity": 65,
            "target_shelf_life_days": 180,
        }
        response = await client.post("/api/recommend", json=payload)
        assert response.status_code == 501, (
            "POST /api/recommend must return 501 until Phase 5 is implemented."
        )

    async def test_get_recommendation_returns_501(self, client: AsyncClient):
        response = await client.get("/api/recommendations/ANALYSIS-001")
        assert response.status_code == 501
