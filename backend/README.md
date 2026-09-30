# PackSense AI — Backend

FastAPI-based decision-support engine for food packaging material recommendation.

**SIH 2026 | Problem Statement SIH26236 | Team eX0n_ | ID 1305-2026 TIGC**

---

## Quick Start

```bash
# From the PackSense-AI/backend directory

# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment config
cp ../.env.example .env   # edit if needed — SQLite default works out of the box

# 4. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/api/docs

Health check: http://localhost:8000/api/health

---

## Running Tests

```bash
# From the backend/ directory, with the venv activated
pytest
```

Expected output for Phase 1:
- All seed data integrity tests pass
- All model unit tests pass
- All API tests pass (health, foods, materials, structures, sources)
- POST /api/analyze and POST /api/recommend return 501 (correct — not yet implemented)

---

## Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app factory + lifespan
│   ├── config.py             # Settings (pydantic-settings, .env)
│   │
│   ├── api/                  # Route handlers (thin — no business logic)
│   │   ├── foods.py
│   │   ├── candidates.py
│   │   ├── analysis.py       # Phase 2+ stub
│   │   └── recommendations.py # Phase 5+ stub
│   │
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── food.py
│   │   ├── material.py
│   │   ├── packaging.py
│   │   ├── rules.py
│   │   ├── regulation.py
│   │   └── source.py
│   │
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── food.py
│   │   ├── analysis.py
│   │   └── recommendation.py
│   │
│   ├── engines/              # Decision pipeline engines (Phase 2–5)
│   │   ├── risk_engine.py         (Phase 2)
│   │   ├── requirement_engine.py  (Phase 2)
│   │   ├── candidate_engine.py    (Phase 3)
│   │   ├── regulatory_engine.py   (Phase 3)
│   │   ├── technical_filter.py    (Phase 3)
│   │   ├── map_engine.py          (Phase 4)
│   │   ├── cost_engine.py         (Phase 4)
│   │   ├── sustainability_engine.py (Phase 4)
│   │   ├── ranking_engine.py      (Phase 5)
│   │   └── explanation_engine.py  (Phase 5)
│   │
│   ├── services/             # Orchestration services (Phase 2–6)
│   │   ├── analysis_service.py
│   │   ├── recommendation_service.py
│   │   └── provenance_service.py
│   │
│   ├── database/             # DB connection, seeder, repositories
│   │   ├── connection.py
│   │   ├── seed.py
│   │   └── repositories/
│   │
│   ├── data/                 # JSON seed fixtures
│   │   ├── foods.json
│   │   ├── materials.json
│   │   ├── material_properties.json
│   │   ├── packaging_structures.json
│   │   ├── rules.json
│   │   ├── regulations.json
│   │   └── sources.json
│   │
│   └── utils/
│       └── logging.py
│
├── tests/
│   ├── conftest.py           # In-memory SQLite fixtures, async HTTP client
│   ├── test_api.py           # Phase 1 API endpoint tests
│   ├── test_models.py        # ORM + schema unit tests
│   └── test_seed.py          # Seed data integrity + scientific correctness
│
├── pytest.ini
└── requirements.txt
```

---

## API Endpoints (Phase 1)

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/health` | ✅ Live | System health check |
| GET | `/api/foods` | ✅ Live | List all food commodities |
| GET | `/api/foods/{id}` | ✅ Live | Get food by ID |
| GET | `/api/materials` | ✅ Live | List all base materials |
| GET | `/api/materials/{id}` | ✅ Live | Get material + properties |
| GET | `/api/packaging-structures` | ✅ Live | List all packaging structures |
| GET | `/api/packaging-structures/{id}` | ✅ Live | Get structure by ID |
| GET | `/api/sources` | ✅ Live | List all evidence sources |
| GET | `/api/sources/{id}` | ✅ Live | Get source by ID |
| POST | `/api/analyze` | 🔄 Phase 2 | Risk + requirements analysis |
| POST | `/api/recommend` | 🔄 Phase 5 | Full recommendation pipeline |
| GET | `/api/recommendations/{id}` | 🔄 Phase 6 | Retrieve stored result |

---

## Database

Default: **SQLite** (`packsense.db`) — created automatically on first run.

To switch to PostgreSQL, set in `.env`:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/packsense
```

Tables are created automatically via SQLAlchemy on startup. Seed data is loaded
idempotently (safe to restart).

---

## Prototype Limitations

- All material property values (OTR, WVTR, CO2TR) are `null` with
  `data_status: NEEDS_VALIDATION`. No scientific values are fabricated.
- Regulatory status for all materials is `REVIEW` — compliance verification
  by a qualified expert is required before production use.
- The recommendation pipeline (Phases 2–5) is not yet implemented.
- No shelf-life prediction is performed or claimed.
- No ML accuracy metrics are displayed.

See `docs/validation.md` for full details on data provenance.

---

## Decision Pipeline (Phases 2–5)

```
Food + Storage Conditions
        ↓
   Food Profile       ← Phase 2
        ↓
   Risk Analysis      ← Phase 2
        ↓
  Requirements        ← Phase 2
        ↓
  Candidate Gen.      ← Phase 3
        ↓
 Regulatory Filter    ← Phase 3
        ↓
 Technical Filter     ← Phase 3
        ↓
  MAP Analysis        ← Phase 4 (fresh produce only)
        ↓
 Cost + Sustainability ← Phase 4
        ↓
 TOPSIS / MCDM        ← Phase 5
        ↓
   Explanation        ← Phase 5
        ↓
  Ranked Results
```
