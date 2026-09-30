"""
Tests verifying the seed data integrity.

These tests confirm that the prototype seed data satisfies the scientific
correctness rules defined in the specification — e.g. no invented values,
correct sensitivity levels, correct regulatory status.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent.parent / "app" / "data"


def load(filename: str) -> list[dict]:
    with (DATA_DIR / filename).open(encoding="utf-8") as f:
        return json.load(f)


# ── Foods seed ─────────────────────────────────────────────────────────────────

class TestFoodsSeed:
    def test_three_prototype_foods_present(self):
        foods = load("foods.json")
        ids = {f["id"] for f in foods}
        assert "FOOD001" in ids
        assert "FOOD002" in ids
        assert "FOOD003" in ids

    def test_potato_chips_profile(self):
        foods = {f["id"]: f for f in load("foods.json")}
        pc = foods["FOOD001"]
        assert pc["name"] == "Potato Chips"
        assert pc["category"] == "snack"
        assert pc["oxygen_sensitivity"] == "HIGH"
        assert pc["moisture_sensitivity"] == "HIGH"
        assert pc["respiration_class"] == "NONE"
        assert pc["fat"] == "HIGH"

    def test_roasted_peanuts_profile(self):
        foods = {f["id"]: f for f in load("foods.json")}
        rp = foods["FOOD002"]
        assert rp["oxygen_sensitivity"] == "HIGH"
        assert rp["respiration_class"] == "NONE"

    def test_tomato_profile(self):
        foods = {f["id"]: f for f in load("foods.json")}
        tom = foods["FOOD003"]
        assert tom["category"] == "fresh_produce"
        assert tom["respiration_class"] == "CLIMACTERIC"
        # Tomato must NOT have max oxygen sensitivity — it needs gas exchange
        assert tom["oxygen_sensitivity"] != "NONE"

    def test_no_invented_numeric_values(self):
        """pH and water_activity must be null — not fabricated numbers."""
        for food in load("foods.json"):
            assert food.get("pH") is None, (
                f"Food {food['id']} has fabricated pH={food['pH']}"
            )
            assert food.get("water_activity") is None, (
                f"Food {food['id']} has fabricated water_activity={food['water_activity']}"
            )

    def test_all_foods_have_source_id(self):
        for food in load("foods.json"):
            assert food.get("source_id"), f"Food {food['id']} missing source_id"


# ── Materials seed ─────────────────────────────────────────────────────────────

class TestMaterialsSeed:
    def test_eight_materials_present(self):
        mats = load("materials.json")
        assert len(mats) >= 8

    def test_no_material_claims_compliant(self):
        """
        CRITICAL: food_contact_status must never be 'compliant' without
        a specific validated standard — all prototype materials use 'review_required'.
        """
        for mat in load("materials.json"):
            assert mat["food_contact_status"] != "compliant", (
                f"Material {mat['id']} claims 'compliant' food contact — "
                "prototype must use 'review_required' pending verification."
            )

    def test_all_materials_have_source_id(self):
        for mat in load("materials.json"):
            assert mat.get("source_id"), f"Material {mat['id']} missing source_id"


# ── Material properties seed ───────────────────────────────────────────────────

class TestMaterialPropertiesSeed:
    def test_properties_have_data_status(self):
        for prop in load("material_properties.json"):
            assert "data_status" in prop, f"Property id={prop['id']} missing data_status"

    def test_needs_validation_properties_have_null_values(self):
        """
        Any property marked NEEDS_VALIDATION or PROTOTYPE_ASSUMPTION
        must not carry a fabricated numeric value.
        """
        for prop in load("material_properties.json"):
            if prop["data_status"] in ("NEEDS_VALIDATION", "PROTOTYPE_ASSUMPTION"):
                assert prop["value"] is None, (
                    f"Property id={prop['id']} ({prop['property']}) has "
                    f"data_status={prop['data_status']} but value={prop['value']} — "
                    "do not fabricate scientific values."
                )

    def test_properties_reference_valid_materials(self):
        mat_ids = {m["id"] for m in load("materials.json")}
        for prop in load("material_properties.json"):
            assert prop["material_id"] in mat_ids, (
                f"Property id={prop['id']} references unknown material_id={prop['material_id']}"
            )


# ── Packaging structures seed ──────────────────────────────────────────────────

class TestPackagingStructuresSeed:
    def test_eight_structures_present(self):
        structs = load("packaging_structures.json")
        assert len(structs) >= 8

    def test_perforated_structures_present(self):
        structs = load("packaging_structures.json")
        types = {s["structure_type"] for s in structs}
        assert "perforated" in types, "No perforated structures — required for MAP/fresh produce"

    def test_no_structure_claims_compliant_food_contact(self):
        for s in load("packaging_structures.json"):
            assert s["food_contact_status"] != "compliant", (
                f"Structure {s['id']} claims compliant food contact without verification"
            )

    def test_structures_have_sustainability_indicators(self):
        for s in load("packaging_structures.json"):
            si = s.get("sustainability_indicators")
            assert si is not None, f"Structure {s['id']} missing sustainability_indicators"
            assert "layer_count" in si, f"Structure {s['id']} missing layer_count"

    def test_high_barrier_structure_present(self):
        """PET/AL/PE (or equivalent high-barrier) must be available for snack evaluation."""
        structs = load("packaging_structures.json")
        al_structures = [
            s for s in structs
            if "AL" in s["name"] or "Aluminium" in str(s.get("layers", []))
        ]
        assert len(al_structures) >= 1, "No aluminium-foil structure found"


# ── Rules seed ────────────────────────────────────────────────────────────────

class TestRulesSeed:
    def test_rules_present(self):
        rules = load("rules.json")
        assert len(rules) >= 10

    def test_rules_have_data_status(self):
        for rule in load("rules.json"):
            assert "data_status" in rule, f"Rule {rule['id']} missing data_status"

    def test_high_oxygen_sensitivity_generates_low_otr_rule(self):
        """Core rule: HIGH oxygen_sensitivity → LOW OTR requirement."""
        rules = load("rules.json")
        matching = [
            r for r in rules
            if r["field_path"] == "oxygen_sensitivity"
            and r["value"] == "HIGH"
            and r["required_property"] == "OTR"
            and r["outcome"] == "LOW"
        ]
        assert len(matching) >= 1, (
            "Missing rule: HIGH oxygen_sensitivity → OTR=LOW. "
            "This is the primary driver for snack food packaging selection."
        )

    def test_climacteric_respiration_requires_gas_exchange(self):
        """MAP rule: CLIMACTERIC respiration → GAS_EXCHANGE REQUIRED."""
        rules = load("rules.json")
        matching = [
            r for r in rules
            if r["field_path"] == "respiration_class"
            and r["value"] == "CLIMACTERIC"
            and r["required_property"] == "GAS_EXCHANGE"
            and r["outcome"] == "REQUIRED"
        ]
        assert len(matching) >= 1, (
            "Missing rule: CLIMACTERIC respiration_class → GAS_EXCHANGE=REQUIRED. "
            "This is essential for the Tomato MAP analysis path."
        )

    def test_respiring_produce_not_max_barrier(self):
        """
        Anti-rule: HIGH/CLIMACTERIC respiration must NOT lead to maximum barrier.
        This rule prevents the naive 'tomato → PET/AL/PE' error.
        """
        rules = load("rules.json")
        matching = [
            r for r in rules
            if r["field_path"] == "respiration_class"
            and isinstance(r["value"], list)
            and "CLIMACTERIC" in r["value"]
            and r["required_property"] == "OTR"
            and r["outcome"] == "MEDIUM"
        ]
        assert len(matching) >= 1, (
            "Missing anti-rule: respiring produce must not require maximum barrier (LOW OTR). "
            "The system must derive a MEDIUM OTR / gas-exchange requirement for fresh produce."
        )


# ── Regulations seed ──────────────────────────────────────────────────────────

class TestRegulationsSeed:
    def test_regulations_present(self):
        regs = load("regulations.json")
        assert len(regs) >= 8

    def test_all_regulations_are_review_not_listed(self):
        """
        Prototype regulations must be REVIEW, never LISTED with a claim of approval.
        Real compliance requires expert verification.
        """
        for reg in load("regulations.json"):
            assert reg["status"] == "REVIEW", (
                f"Regulation {reg['id']} has status={reg['status']} — "
                "prototype must use REVIEW; claiming LISTED implies verified compliance "
                "which is not established for this prototype."
            )

    def test_regulations_reference_fssai(self):
        regs = load("regulations.json")
        fssai_regs = [r for r in regs if "FSSAI" in r["standard"]]
        assert len(fssai_regs) >= 6, "Expected FSSAI regulation records for primary materials"


# ── Sources seed ──────────────────────────────────────────────────────────────

class TestSourcesSeed:
    def test_sources_present(self):
        sources = load("sources.json")
        assert len(sources) >= 6

    def test_fssai_source_present(self):
        sources = load("sources.json")
        fssai_sources = [
            s for s in sources
            if "FSSAI" in s["title"] or "FSSAI" in (s.get("publisher") or "")
        ]
        assert len(fssai_sources) >= 1

    def test_prototype_source_has_needs_validation(self):
        sources = {s["source_id"]: s for s in load("sources.json")}
        proto = sources.get("SRC-PROTO-001")
        assert proto is not None
        assert proto["evidence_quality"] == "NEEDS_VALIDATION"

    def test_all_sources_have_title(self):
        for src in load("sources.json"):
            assert src.get("title"), f"Source {src['source_id']} missing title"
