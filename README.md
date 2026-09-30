# PackSense AI

**AI-Based Intelligent Food Packaging Material Recommendation System**

| Field | Value |
|-------|-------|
| Problem Statement ID | SIH26236 |
| Organisation | Ministry of Food Processing Industries |
| Theme | Agriculture, FoodTech & Rural Development |
| Category | Software |
| Team | eX0n_ |
| Team ID | 1305-2026 TIGC |
| Event | Smart India Hackathon 2026 |

---

## What It Does

PackSense AI is a structured engineering decision-support system that recommends food packaging materials by reasoning from first principles — not by lookup tables.

The recommendation pipeline is:

```
Food Commodity + Storage Conditions
            ↓
      Food Profile
            ↓
      Risk Analysis          (oxidation, moisture, microbial, respiration, light)
            ↓
  Packaging Requirements     (OTR, WVTR, sealability, gas exchange)
            ↓
   Candidate Generation
            ↓
   Regulatory Screening      (FSSAI / BIS — review required, not approval claimed)
            ↓
   Technical Filtering       (PASS / FAIL / REVIEW per requirement)
            ↓
  MAP / Performance Analysis (fresh produce only)
            ↓
  Cost + Sustainability      (indicator-based, no fake precision)
            ↓
   TOPSIS / MCDM Ranking
            ↓
  Explainable Recommendation + Evidence
```

Every recommendation is fully traceable:
> *Food characteristics → degradation risks → packaging requirements → candidate evaluation → ranking → evidence sources.*

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI, Pydantic |
| Database | SQLite (dev) / PostgreSQL (production) |
| ORM | SQLAlchemy (async) |
| Ranking | TOPSIS / MCDM (NumPy, SciPy) |
| Testing | pytest, pytest-asyncio |

---

## Project Structure

```
PackSense-AI/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/              # Route handlers
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── engines/          # Decision pipeline engines
│   │   ├── services/         # Orchestration services
│   │   ├── database/         # Connection, seed, repositories
│   │   └── data/             # JSON seed fixtures
│   ├── tests/
│   └── requirements.txt
│
├── frontend/                 # React + TypeScript UI (Phase 7+)
│   └── src/
│
├── docs/                     # Architecture and validation docs
│   ├── architecture.md
│   ├── data-model.md
│   ├── recommendation-engine.md
│   ├── api.md
│   └── validation.md
│
├── .env.example
└── docker-compose.yml        (Phase 8+)
```

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+ (frontend, Phase 7+)

### Backend Setup

```bash
cd PackSense-AI/backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux / macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
copy ..\\.env.example .env
```

### Running the Backend

```bash
# From backend/ with venv active
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/api/health
- ReDoc: http://localhost:8000/api/redoc

### Running Tests

```bash
# From backend/ with venv active
pytest
```

---

## Prototype Foods (Phase 1 Seed Data)

| ID | Food | Category | Key Risk |
|----|------|----------|----------|
| FOOD001 | Potato Chips | Snack | Oxidation HIGH, Moisture HIGH |
| FOOD002 | Roasted Peanuts | Snack | Oxidation HIGH, Moisture MEDIUM |
| FOOD003 | Tomato | Fresh Produce | Respiration CLIMACTERIC, MAP required |

---

## Development Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Project structure, models, seed data, health endpoint | ✅ Complete |
| 2 | Risk Engine, Requirement Engine | 🔄 Next |
| 3 | Candidate Engine, Regulatory Filter, Technical Filter | Pending |
| 4 | MAP Engine, Cost Engine, Sustainability Engine | Pending |
| 5 | TOPSIS Ranking, Explanation Engine | Pending |
| 6 | Full API integration, end-to-end tests | Pending |
| 7 | React frontend | Pending |
| 8 | Frontend ↔ Backend integration | Pending |
| 9 | Demo polish | Pending |
| 10 | Final test suite | Pending |

---

## Scientific Integrity Principles

This prototype follows strict data integrity rules:

- **No invented property values** — OTR, WVTR, and all material properties are `null` with `data_status: NEEDS_VALIDATION` until experimentally validated
- **No fake regulatory approval** — all materials have status `REVIEW_REQUIRED`; regulatory screening flags what requires verification, it does not confer legal approval
- **No fake shelf-life prediction** — target shelf life is a user-entered design requirement, not a system prediction
- **No fake ML accuracy** — no percentage confidence scores without a validated evaluation methodology
- **Full traceability** — every scientific value references a `source_id` with evidence quality rating

---

## Data Provenance

Every scientific value in the system carries an explicit `data_status`:

| Status | Meaning |
|--------|---------|
| `VALIDATED` | Experimentally verified from a peer-reviewed source |
| `SOURCE_REQUIRED` | Value present but source reference missing |
| `PROTOTYPE_ASSUMPTION` | Working assumption — must be validated before production use |
| `NEEDS_VALIDATION` | Placeholder `null` — no value assigned |

**Phase 1 status:** All material property values (OTR, WVTR, CO2TR) are `null` with `data_status: NEEDS_VALIDATION`. No scientific barrier values are fabricated. See `docs/validation.md` for full details.

### Prototype vs Validated Data

The system **cannot silently fall back** from validated data to prototype assumptions. Every API response includes `data_status` on each value and `validation_notes` in analysis responses, so the caller always knows which values are experimentally confirmed and which are prototype placeholders.

---

## Prototype Disclaimer

> This system is a prototype developed for Smart India Hackathon 2026.
> All scientific values marked `PROTOTYPE_ASSUMPTION` or `NEEDS_VALIDATION`
> require experimental validation before use in production packaging decisions.
> Regulatory screening does not constitute legal compliance verification.
> No shelf-life predictions are made.

---

## Team

**eX0n_** | Team ID: 1305-2026 TIGC | Smart India Hackathon 2026
