# PackSense AI — System Architecture

**SIH 2026 | Team eX0n_ | Problem Statement SIH26236**

---

## Overview

PackSense AI is a structured engineering decision-support system for food packaging material selection. It is NOT a chatbot or a lookup table — it executes a deterministic multi-step reasoning pipeline from food characteristics to ranked packaging candidates.

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│             USER / UI LAYER                 │
│         React + TypeScript (Phase 7+)       │
└──────────────────────┬──────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────┐
│           FastAPI APPLICATION LAYER          │
│  /api/health  /api/foods  /api/analyze       │
│  /api/recommend  /api/materials  /api/sources│
└──────────────────────┬──────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────┐ ┌────────────┐ ┌──────────────┐
│ Risk Engine │ │ Requirement│ │  Regulatory  │
│  (Phase 2)  │ │   Engine   │ │   Engine     │
│             │ │  (Phase 2) │ │  (Phase 3)   │
└──────┬──────┘ └─────┬──────┘ └──────┬───────┘
       └──────────────┼───────────────┘
                      ▼
            ┌──────────────────┐
            │ Candidate Engine │
            │   (Phase 3)      │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │ Technical Filter │
            │   (Phase 3)      │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │  MAP / Respira-  │
            │  tion Engine     │
            │   (Phase 4)      │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │ Cost + Sustain-  │
            │ ability Engine   │
            │   (Phase 4)      │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │ TOPSIS / MCDM    │
            │ Ranking Engine   │
            │   (Phase 5)      │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │ Explanation      │
            │ Engine (Phase 5) │
            └────────┬─────────┘
                     ▼
            ┌──────────────────────────────┐
            │  Ranked Candidates           │
            │  + Evidence                  │
            │  + Alternatives              │
            │  + Rejection Reasons         │
            │  + Validation Notes          │
            └──────────────────────────────┘

                    ▲
                    │
          ┌─────────┴──────────┐
          │     DATA LAYER     │
          │                    │
          │  Foods             │
          │  Materials         │
          │  Material Props    │
          │  Pkg Structures    │
          │  Rules             │
          │  Regulations       │
          │  Sources           │
          └────────────────────┘
```

---

## Decision Pipeline (12 Steps)

| Step | Component | Phase | Description |
|------|-----------|-------|-------------|
| 1 | Food Profile | 2 | Load food characteristics from DB |
| 2 | Risk Analysis | 2 | Deterministic risk scoring (oxidation, moisture, microbial, respiration, light) |
| 3 | Requirements | 2 | Derive OTR/WVTR/sealability/gas-exchange requirements from risk vector |
| 4 | Candidate Gen | 3 | Select relevant packaging structures for the food category |
| 5 | Regulatory Filter | 3 | Screen candidates against FSSAI/BIS — PASS/REVIEW/FAIL |
| 6 | Technical Filter | 3 | Compare candidate properties against requirements — PASS/FAIL/REVIEW |
| 7 | MAP Analysis | 4 | Gas-exchange analysis for respiring fresh produce (tomato etc.) |
| 8 | Cost Estimate | 4 | Indicator-based cost comparison (no fake precision) |
| 9 | Sustainability | 4 | Recyclability, layer count, material complexity indicators |
| 10 | TOPSIS Ranking | 5 | Multi-criteria decision making with configurable weights |
| 11 | Explanation | 5 | Traceable chain: food risk → requirement → candidate → ranking |
| 12 | Response | 6 | Ranked results + alternatives + rejected candidates + evidence |

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend framework | FastAPI | 0.115.6 |
| Data validation | Pydantic | 2.10.3 |
| ORM | SQLAlchemy (async) | 2.0.36 |
| DB (dev) | SQLite + aiosqlite | 0.20.0 |
| DB (prod) | PostgreSQL + asyncpg | 0.30.0 |
| Ranking | NumPy + SciPy (Phase 5) | — |
| Testing | pytest + pytest-asyncio | 8.3.4 / 0.24.0 |
| Frontend | React + TypeScript + Vite | Phase 7 |

---

## Data Flow

```
POST /api/recommend
{food_id, temperature, relative_humidity, target_shelf_life_days, ranking_weights}
        │
        ▼
RecommendationService.execute()
        │
        ├── FoodRepository.get_by_id()         → Food ORM object
        ├── RiskEngine.analyse()                → RiskVector
        ├── RequirementEngine.derive()          → [RequirementEntry]
        ├── CandidateEngine.generate()          → [PackagingStructure]
        ├── RegulatoryEngine.filter()           → [CandidateEvaluation]
        ├── TechnicalFilter.filter()            → [CandidateEvaluation]
        ├── MAPEngine.analyse() (if applicable) → MAPAnalysis
        ├── CostEngine.evaluate()               → cost indicators
        ├── SustainabilityEngine.evaluate()     → sustainability indicators
        ├── RankingEngine.rank() [TOPSIS]       → [RankedCandidate]
        └── ExplanationEngine.explain()         → [str] reasons
        │
        ▼
RecommendationResponse (JSON)
```

---

## Database Schema (Phase 1)

```
sources          ← bibliographic / evidence provenance
foods            ← food commodities with sensitivity profiles
materials        ← packaging substrates (PET, BOPP, PE, AL, etc.)
material_properties  ← OTR, WVTR, CO2TR etc. with data_status
packaging_structures ← multi-layer formats (PET/PE, BOPP/MetBOPP/PE etc.)
packaging_rules  ← deterministic requirement derivation rules
regulations      ← FSSAI/BIS regulatory screening records
```

All tables support async queries via SQLAlchemy async engine. Database is SQLite for local development; swap `DATABASE_URL` in `.env` for PostgreSQL in production.

---

## Scientific Integrity

The architecture is designed so that:

1. **Rules, not heuristics** — requirements are derived from a rule table, not hard-coded `if food == X: return Y`
2. **Data status propagation** — every scientific value carries `data_status` through the entire pipeline into the response
3. **No silent fabrication** — `null` values with `NEEDS_VALIDATION` are explicitly represented rather than filled with guesses
4. **Reproducibility** — same input + same database = same output (no random elements in the core pipeline)
5. **Traceability** — every recommendation links back through rules → candidate properties → sources

See `docs/validation.md` for the full data provenance policy.
