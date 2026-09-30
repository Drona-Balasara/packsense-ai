# PackSense AI — Data Provenance and Validation Status

**SIH 2026 | Team eX0n_ | Phase 1**

---

## Critical Principle

PackSense AI explicitly distinguishes between **prototype assumptions** and **validated evidence**. This distinction is enforced at the data layer and surfaced in every API response and UI element.

**The system must never silently fall back from validated data to prototype data without informing the user.**

---

## Data Status Taxonomy

Every scientific value in the system carries a `data_status` field with one of four values:

| Status | Meaning | Action Required |
|--------|---------|----------------|
| `VALIDATED` | Experimentally verified value from a peer-reviewed source with documented test conditions | None — may be used directly |
| `SOURCE_REQUIRED` | Value is plausible but source reference is missing | Locate and attach source before use |
| `PROTOTYPE_ASSUMPTION` | Working engineering assumption used during development | Must be replaced with validated data before production use |
| `NEEDS_VALIDATION` | Placeholder — no value assigned; experimental measurement required | Do not use in production decisions |

---

## Current Phase 1 Status

### Material Properties (OTR, WVTR, CO2TR, etc.)

**ALL material property values in Phase 1 are `NEEDS_VALIDATION`.**

Specific OTR and WVTR values are NOT present in the database. The `value` field is `null` for all prototype material properties.

Reason: Barrier property values vary by:
- Material grade and supplier
- Film thickness
- Processing conditions (biaxial orientation, metallisation quality)
- Test temperature and humidity
- Test method (ASTM D3985, ASTM E96, ISO 15105-2, etc.)

Reproducing generic literature values without specifying all of the above would constitute fabrication of scientific data. The system does not do this.

**To add validated values**: Obtain supplier datasheets or peer-reviewed measurement data, add a `Source` record, and update the `MaterialProperty` record with `data_status: VALIDATED`, `value`, `unit`, `test_method`, `temperature`, `humidity`, `thickness`, and `source_id`.

### Food Profiles

All food profile attributes (moisture, fat, oxygen_sensitivity, etc.) are **qualitative** (`HIGH`, `MEDIUM`, `LOW`) with `source_id: SRC-PROTO-001`.

Numeric values for `pH` and `water_activity` are `null` — not fabricated.

### Rules

All 14 rules in Phase 1 carry `data_status: PROTOTYPE_ASSUMPTION`. The qualitative logic (e.g. HIGH oxygen sensitivity → LOW OTR requirement) is scientifically defensible, but the absence of numeric thresholds means the rules operate at a qualitative level only.

### Regulations

All 8 regulation records have `status: REVIEW`. No material is claimed as "FSSAI Approved" in a generic sense. The records indicate which standard is relevant and that verification is required.

---

## Separation Enforcement

### API Layer

- `data_status` is returned in every material property response
- `prototype_disclaimer` is included in every health response
- Recommendation responses (Phase 5+) will include `validation_notes` listing all prototype assumptions used in a given analysis

### Test Enforcement

The test suite (`test_seed.py`) enforces the separation with automated checks:

```
test_needs_validation_properties_have_null_values  — no fabricated numbers
test_no_material_claims_compliant                  — no fake regulatory approval
test_all_regulations_are_review_not_listed         — no fake compliance
test_rules_have_data_status                        — all rules labelled
test_prototype_source_has_needs_validation         — prototype source correctly labelled
```

These tests will **fail** if anyone attempts to insert fabricated scientific values.

---

## Upgrade Path: Prototype → Validated

To upgrade a value from prototype to validated:

1. Obtain the measurement from a peer-reviewed paper, standard test report, or verified supplier datasheet
2. Add a `Source` record to `sources.json` with `evidence_quality: HIGH` or `MEDIUM`
3. Update the `MaterialProperty` record:
   - Set `value` to the measured value
   - Set `unit`, `temperature`, `humidity`, `thickness`, `test_method`
   - Set `source_id` to the new source
   - Set `data_status: VALIDATED`
4. Re-run the test suite — tests will verify the update is internally consistent
5. The recommendation engine will automatically use the validated value and reflect the improved evidence quality in the ranking

---

## What Is Never Claimed

| Claim | Status |
|-------|--------|
| Exact OTR/WVTR values for specific materials | NOT claimed — `null` with `NEEDS_VALIDATION` |
| FSSAI approval for any material | NOT claimed — `REVIEW` status only |
| Predicted shelf life | NOT claimed — target shelf life is a user input |
| ML accuracy percentage | NOT claimed — no ML model trained |
| Experimentally validated barrier performance | NOT claimed in Phase 1 |

---

## Sources

See `backend/app/data/sources.json` for all bibliographic references.

Key sources referenced in Phase 1:
- `SRC-FSSAI-PKG-2018` — FSSAI Packaging Regulations 2018 (regulatory screening)
- `SRC-ROBERTSON-2013` — Robertson, Food Packaging Principles and Practice (qualitative rules)
- `SRC-MAP-PRODUCE-2019` — MAP for fresh produce (tomato/respiration rules)
- `SRC-PROTO-001` — Internal prototype assumptions (all NEEDS_VALIDATION)
