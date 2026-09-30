# PackSense AI — Recommendation Engine

**Phase implementation guide for the decision pipeline.**

---

## Principle: Requirement-First Selection

The engine never maps `food → packaging` directly.

It first answers: **What does this food require?**
Then answers: **Which structures satisfy those requirements?**

```
Food + Storage Conditions
        ↓
   Food Profile
        ↓
   Risk Analysis         ← "What can go wrong?"
        ↓
   Requirements          ← "What must the packaging do?"
        ↓
   Candidate Pool        ← "Which structures are candidates?"
        ↓
   Regulatory Filter     ← "Which are legally screenable?"
        ↓
   Technical Filter      ← "Which meet the requirements?"
        ↓
   MAP Analysis          ← "For respiring produce — gas balance?"
        ↓
   Cost + Sustainability ← "Economic and environmental indicators"
        ↓
   TOPSIS Ranking        ← "Which is best overall?"
        ↓
   Explanation           ← "Why?"
```

---

## Phase 2 — Risk Engine

**File:** `backend/app/engines/risk_engine.py`

Inputs: `FoodProfile`, `StorageConditions`

Output:
```json
{
  "food_id": "FOOD001",
  "risks": {
    "oxidation":   {"level": "HIGH",   "reasoning": "...", "data_status": "PROTOTYPE_ASSUMPTION"},
    "moisture":    {"level": "HIGH",   "reasoning": "...", "data_status": "PROTOTYPE_ASSUMPTION"},
    "microbial":   {"level": "LOW",    "reasoning": "...", "data_status": "PROTOTYPE_ASSUMPTION"},
    "respiration": {"level": "NONE",   "reasoning": "...", "data_status": "PROTOTYPE_ASSUMPTION"},
    "light":       {"level": "MEDIUM", "reasoning": "...", "data_status": "PROTOTYPE_ASSUMPTION"}
  }
}
```

Logic: Apply rules from `packaging_rules` table against food attributes. Rule evaluation is deterministic and traceable.

---

## Phase 2 — Requirement Engine

**File:** `backend/app/engines/requirement_engine.py`

Inputs: `RiskVector`, `FoodProfile`, `StorageConditions`

Output:
```json
[
  {"property": "OTR",        "requirement": "LOW",      "reason": "High oxidation sensitivity"},
  {"property": "WVTR",       "requirement": "LOW",      "reason": "High moisture sensitivity"},
  {"property": "SEALABILITY","requirement": "HIGH",     "reason": "Package integrity for barrier"},
  {"property": "GAS_EXCHANGE","requirement": "NOT_REQUIRED", "reason": "Non-respiring food"}
]
```

---

## Phase 3 — Candidate Engine

**File:** `backend/app/engines/candidate_engine.py`

Generates a relevant subset of `packaging_structures` based on food category and requirements. Does NOT return all structures blindly.

---

## Phase 3 — Regulatory Engine

**File:** `backend/app/engines/regulatory_engine.py`

Checks each candidate's material_ids against `regulations` table.

Output per candidate: `LISTED` / `REVIEW` / `NOT_LISTED`

**Never claims approval. Only flags what requires verification.**

---

## Phase 3 — Technical Filter

**File:** `backend/app/engines/technical_filter.py`

Compares required properties against known material properties.

- If property data exists and satisfies requirement → `PASS`
- If property data exists and fails requirement → `FAIL`
- If property data is missing or `NEEDS_VALIDATION` → `REVIEW` (not `FAIL`)

---

## Phase 4 — MAP Engine

**File:** `backend/app/engines/map_engine.py`

Applies only to foods with `respiration_class` in `[HIGH, CLIMACTERIC]`.

Conceptual analysis:
```
Respiration rate (O2 consumption, CO2 generation)
        +
Packaging permeability (OTR, CO2TR)
        +
Storage temperature
        ↓
Equilibrium atmosphere estimate
        ↓
Assessment: breathable / perforated / standard MAP film
```

Output is labelled `PROTOTYPE_ESTIMATION` — not a validated shelf-life prediction.

---

## Phase 5 — TOPSIS Ranking

**File:** `backend/app/engines/ranking_engine.py`

Only candidates that survive regulatory and technical hard constraints enter TOPSIS.

Decision matrix criteria:

| Criterion | Default Weight | Description |
|-----------|---------------|-------------|
| technical_fit | 0.40 | How well candidate meets requirements |
| cost | 0.20 | Cost indicator (lower = better) |
| sustainability | 0.20 | Recyclability, layer count, biodegradability |
| evidence_quality | 0.20 | Data completeness and source quality |

Weights are user-configurable and clearly labelled as prototype defaults.

TOPSIS procedure:
1. Construct decision matrix
2. Normalise (vector normalisation)
3. Apply weights
4. Identify ideal best and ideal worst
5. Calculate separation distances
6. Calculate closeness coefficient
7. Rank by closeness (higher = better)

---

## Phase 5 — Explanation Engine

**File:** `backend/app/engines/explanation_engine.py`

Generates a traceable explanation chain for each ranked candidate:

```
1. [Food] has [characteristic]
2. This creates [risk level] [risk type] risk
3. Therefore [property] requirement is [level]
4. [Candidate] [satisfies/does not satisfy] this requirement
5. Regulatory status: [REVIEW/LISTED/NOT_LISTED]
6. Evidence quality: [HIGH/MEDIUM/LOW/NEEDS_VALIDATION]
7. Cost indicator: [LOW/MEDIUM/HIGH/UNAVAILABLE]
8. TOPSIS score: [score] (rank [n] of [total])
```

The explanation must be derivable mechanically from the pipeline outputs — not generated by an LLM.
