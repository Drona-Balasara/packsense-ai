"""
Unit tests for ORM models and Pydantic schemas.

Verifies that:
  - Models instantiate correctly with seed-like data
  - Enums are valid
  - DataStatus is properly propagated
  - No fabricated scientific values are encoded in model defaults
"""

from __future__ import annotations

import pytest

from app.models.food import Food, FoodCategory, RespirationClass, SensitivityLevel
from app.models.material import DataStatus, FoodContactStatus, Material, MaterialProperty
from app.models.packaging import PackagingStructure, StructureType
from app.models.regulation import RegStatus, Regulation
from app.models.rules import PackagingRule
from app.models.source import EvidenceQuality, Source, SourceType
from app.schemas.analysis import AnalyzeRequest, RankingWeights, RecommendRequest
from app.schemas.food import FoodSchema


# ── Enum completeness ──────────────────────────────────────────────────────────

class TestEnums:
    def test_sensitivity_levels(self):
        levels = {e.value for e in SensitivityLevel}
        assert {"NONE", "LOW", "MEDIUM", "HIGH"}.issubset(levels)

    def test_respiration_classes(self):
        classes = {e.value for e in RespirationClass}
        assert "CLIMACTERIC" in classes
        assert "NONE" in classes

    def test_food_categories(self):
        cats = {e.value for e in FoodCategory}
        assert "snack" in cats
        assert "fresh_produce" in cats

    def test_data_status_values(self):
        statuses = {e.value for e in DataStatus}
        assert statuses == {
            "VALIDATED",
            "SOURCE_REQUIRED",
            "PROTOTYPE_ASSUMPTION",
            "NEEDS_VALIDATION",
        }

    def test_reg_status_values(self):
        statuses = {e.value for e in RegStatus}
        assert statuses == {"LISTED", "REVIEW", "NOT_LISTED"}

    def test_evidence_quality_values(self):
        qualities = {e.value for e in EvidenceQuality}
        assert "NEEDS_VALIDATION" in qualities
        assert "HIGH" in qualities

    def test_food_contact_status_no_blanket_compliant(self):
        """
        FoodContactStatus.COMPLIANT exists but must require a named standard.
        The default in models must be REVIEW_REQUIRED, not COMPLIANT.
        """
        assert FoodContactStatus.REVIEW_REQUIRED.value == "review_required"


# ── Food model ─────────────────────────────────────────────────────────────────

class TestFoodModel:
    def test_food_instantiation(self):
        food = Food(
            id="TEST001",
            name="Test Food",
            category=FoodCategory.SNACK.value,
            moisture=SensitivityLevel.LOW.value,
            fat=SensitivityLevel.HIGH.value,
            respiration_class=RespirationClass.NONE.value,
            oxygen_sensitivity=SensitivityLevel.HIGH.value,
            moisture_sensitivity=SensitivityLevel.HIGH.value,
            light_sensitivity=SensitivityLevel.MEDIUM.value,
            microbial_sensitivity=SensitivityLevel.LOW.value,
        )
        assert food.id == "TEST001"
        assert food.name == "Test Food"

    def test_food_nullable_numeric_fields(self):
        """pH and water_activity must be nullable — never fabricated defaults."""
        food = Food(
            id="TEST002",
            name="Test Food 2",
            category=FoodCategory.SNACK.value,
        )
        assert food.pH is None
        assert food.water_activity is None

    def test_food_repr(self):
        food = Food(id="TEST003", name="Repr Test", category="snack")
        assert "TEST003" in repr(food)


# ── Material model ─────────────────────────────────────────────────────────────

class TestMaterialModel:
    def test_material_default_food_contact_status(self):
        """Default must be review_required, never compliant."""
        mat = Material(id="MATTEST", name="Test Material")
        assert mat.food_contact_status == FoodContactStatus.REVIEW_REQUIRED.value

    def test_material_property_default_data_status(self):
        """Default data_status for a property must be PROTOTYPE_ASSUMPTION."""
        prop = MaterialProperty(
            material_id="MATTEST",
            property="OTR",
        )
        assert prop.data_status == DataStatus.PROTOTYPE_ASSUMPTION.value

    def test_material_property_value_nullable(self):
        """OTR/WVTR values must be nullable — prototype never invents numbers."""
        prop = MaterialProperty(
            material_id="MATTEST",
            property="OTR",
            value=None,
            data_status=DataStatus.NEEDS_VALIDATION.value,
        )
        assert prop.value is None

    def test_material_repr(self):
        mat = Material(id="MATTEST2", name="Repr Material")
        assert "MATTEST2" in repr(mat)


# ── PackagingStructure model ───────────────────────────────────────────────────

class TestPackagingStructureModel:
    def test_structure_instantiation(self):
        s = PackagingStructure(
            id="PKGTEST",
            name="Test/PE",
            layers=["Test (outer)", "PE (inner)"],
            sealant="PE",
            structure_type=StructureType.FLEXIBLE_LAMINATE.value,
            material_ids=["MAT001", "MAT002"],
        )
        assert s.id == "PKGTEST"
        assert len(s.layers) == 2

    def test_structure_default_food_contact_review(self):
        s = PackagingStructure(id="PKGTEST2", name="Test2")
        assert s.food_contact_status == "review_required"


# ── Source model ──────────────────────────────────────────────────────────────

class TestSourceModel:
    def test_source_default_evidence_quality(self):
        src = Source(
            source_id="SRC-TEST",
            title="Test Source",
        )
        assert src.evidence_quality == EvidenceQuality.NEEDS_VALIDATION.value

    def test_source_default_type(self):
        src = Source(
            source_id="SRC-TEST2",
            title="Test Source 2",
        )
        assert src.source_type == SourceType.PROTOTYPE_ASSUMPTION.value


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class TestAnalyzeRequestSchema:
    def test_valid_request(self):
        req = AnalyzeRequest(
            food_id="FOOD001",
            temperature=30,
            relative_humidity=65,
            target_shelf_life_days=180,
        )
        assert req.food_id == "FOOD001"
        assert req.temperature == 30

    def test_temperature_bounds(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            AnalyzeRequest(
                food_id="FOOD001",
                temperature=100,  # > 60 — invalid
                relative_humidity=65,
                target_shelf_life_days=180,
            )

    def test_humidity_bounds(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            AnalyzeRequest(
                food_id="FOOD001",
                temperature=30,
                relative_humidity=110,  # > 100 — invalid
                target_shelf_life_days=180,
            )

    def test_shelf_life_positive(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            AnalyzeRequest(
                food_id="FOOD001",
                temperature=30,
                relative_humidity=65,
                target_shelf_life_days=0,  # < 1 — invalid
            )


class TestRankingWeightsSchema:
    def test_default_weights_sum_to_one(self):
        w = RankingWeights()
        total = w.technical_fit + w.cost + w.sustainability + w.evidence_quality
        assert abs(total - 1.0) < 0.01

    def test_invalid_weights_rejected(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            RankingWeights(
                technical_fit=0.5,
                cost=0.5,
                sustainability=0.5,
                evidence_quality=0.5,  # sum = 2.0 — invalid
            )

    def test_custom_valid_weights(self):
        w = RankingWeights(
            technical_fit=0.50,
            cost=0.20,
            sustainability=0.15,
            evidence_quality=0.15,
        )
        total = w.technical_fit + w.cost + w.sustainability + w.evidence_quality
        assert abs(total - 1.0) < 0.01


class TestFoodSchema:
    def test_from_orm_object(self):
        food = Food(
            id="FOOD001",
            name="Potato Chips",
            category="snack",
            moisture="LOW",
            fat="HIGH",
            respiration_class="NONE",
            oxygen_sensitivity="HIGH",
            moisture_sensitivity="HIGH",
            light_sensitivity="MEDIUM",
            microbial_sensitivity="LOW",
        )
        schema = FoodSchema.model_validate(food)
        assert schema.id == "FOOD001"
        assert schema.name == "Potato Chips"
        assert schema.pH is None
        assert schema.water_activity is None
