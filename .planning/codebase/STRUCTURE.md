# Codebase Structure

**Analysis Date:** 2026-03-28

## Directory Layout

```
FreightScope/                        # Repo root
├── backend/                         # Python FastAPI application
│   ├── app/                         # Application package
│   │   ├── api/                     # FastAPI route handlers (one file per domain)
│   │   │   ├── __init__.py
│   │   │   ├── risk.py              # GET /api/risk/{shipment_id}
│   │   │   ├── shipments.py         # GET /api/shipments
│   │   │   ├── upload.py            # POST /api/upload
│   │   │   └── ws.py                # WS /status/{task_id}
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── document.py          # Document + DocType enum
│   │   │   ├── risk_result.py       # RiskResult (JSONB fields)
│   │   │   └── shipment.py          # Shipment + ShipmentStatus enum
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── risk.py              # RiskCard, DelayForecastDay
│   │   │   ├── shipment.py          # ShipmentRead
│   │   │   └── upload.py            # UploadResponse
│   │   ├── services/                # Pure business logic / external clients
│   │   │   ├── __init__.py
│   │   │   ├── countries.py         # REST Countries API client
│   │   │   ├── hf_client.py         # HF Inference API (infer / infer_image)
│   │   │   ├── risk_scorer.py       # Fused score computation (numpy)
│   │   │   └── weather.py           # OpenWeatherMap client
│   │   ├── workers/                 # Celery async task definitions
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py        # Celery instance + queue routing
│   │   │   ├── doc_worker.py        # Invoice PDF -> LayoutLMv3 QA
│   │   │   ├── image_worker.py      # Cargo image -> ViT classification
│   │   │   └── ner_worker.py        # Carrier note -> bert-base-NER + MiniLM dedup
│   │   ├── __init__.py
│   │   ├── config.py                # pydantic-settings Settings singleton
│   │   ├── database.py              # SQLAlchemy async engine + Base + get_db
│   │   └── main.py                  # FastAPI app factory, router registration, CORS
│   ├── migrations/                  # Alembic migration environment
│   │   ├── env.py                   # Async migration runner
│   │   └── versions/                # Migration version scripts (gitkeep placeholder)
│   ├── tests/                       # Backend test suite
│   │   ├── __init__.py
│   │   ├── test_api.py              # Integration tests (httpx ASGITransport)
│   │   └── test_workers.py          # Worker unit tests
│   ├── alembic.ini                  # Alembic config (points to migrations/)
│   └── requirements.txt             # Python dependencies (pinned with >=)
├── frontend/                        # React 18 + Vite SPA
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts            # Typed fetch wrapper; exports `api` object
│   │   ├── components/              # UI components (one directory per component)
│   │   │   ├── IncidentFeed/
│   │   │   │   └── IncidentFeed.tsx # Derives incidents from RiskCard data
│   │   │   ├── MapView/
│   │   │   │   └── MapView.tsx      # react-leaflet map with port markers
│   │   │   ├── RiskCard/
│   │   │   │   └── RiskCard.tsx     # Score badge + recharts line/bar charts
│   │   │   └── UploadZone/
│   │   │       └── UploadZone.tsx   # Multi-file upload form + task status
│   │   ├── hooks/                   # React Query + WebSocket custom hooks
│   │   │   ├── useRiskCard.ts       # useQuery wrapper for /api/risk/{id}
│   │   │   ├── useShipments.ts      # useQuery wrapper for /api/shipments
│   │   │   └── useTaskStatus.ts     # WebSocket hook for Celery task polling
│   │   ├── types/
│   │   │   └── index.ts             # All shared TypeScript interfaces/types
│   │   ├── App.tsx                  # Root layout: sidebar + MapView + detail panel
│   │   └── main.tsx                 # ReactDOM.createRoot + QueryClientProvider
│   ├── index.html                   # Vite HTML entry point
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts               # Vite dev server with /api and /status proxies
├── .env.example                     # Root-level env template
├── .gitignore
└── docker-compose.yml               # postgres:16, redis:7, flower:2.0
```

## Key File Locations

**Backend Entry Points:**
- `backend/app/main.py`: FastAPI app instance, middleware, router registration, startup hook
- `backend/app/config.py`: `Settings` singleton — import this for all env access
- `backend/app/database.py`: `Base`, `engine`, `AsyncSessionLocal`, `get_db` dependency

**Frontend Entry Points:**
- `frontend/src/main.tsx`: ReactDOM mount, `QueryClientProvider` wrapper
- `frontend/src/App.tsx`: Root layout and top-level state (`selectedShipment`)

**Configuration:**
- `backend/app/config.py`: All env vars declared here
- `frontend/vite.config.ts`: Dev proxy rules (`/api` and `/status` -> port 8000)
- `docker-compose.yml`: Infrastructure services (postgres, redis, flower)

**Core Logic:**
- `backend/app/services/hf_client.py`: All HF Inference API calls go through `infer()` or `infer_image()`
- `backend/app/services/risk_scorer.py`: `compute_fused_score(RiskSignals)` -> float 0–1
- `backend/app/workers/celery_app.py`: Queue routing table

**Type Contracts:**
- `frontend/src/types/index.ts`: Mirrors backend Pydantic schemas (kept in sync manually)

## Naming Conventions

**Backend:**
- Files: snake_case (`risk_scorer.py`, `hf_client.py`)
- ORM models: PascalCase matching table singular (`Shipment`, `RiskResult`)
- Pydantic schemas: PascalCase with role suffix (`ShipmentRead`, `RiskCard`, `UploadResponse`)
- Enums: PascalCase + suffix (`ShipmentStatus`, `DocType`)

**Frontend:**
- Components: PascalCase directory + matching `.tsx` (`RiskCard/RiskCard.tsx`)
- Hooks: camelCase with `use` prefix (`useRiskCard.ts`)
- Types: PascalCase interfaces in `types/index.ts`
- Constants: SCREAMING_SNAKE_CASE (`PORT_COORDS`, `SEVERITY_COLOR`)

## Where to Add New Code

**New API endpoint:** Add route to `backend/app/api/<domain>.py`, register in `main.py`, add Pydantic schema, mirror type in `frontend/src/types/index.ts`

**New Celery worker:** Create `backend/app/workers/<name>_worker.py`, add to `include` list in `celery_app.py`, add queue routing

**New external service:** Add `backend/app/services/<name>.py` with async functions only

**New SQLAlchemy model:** Create `backend/app/models/<noun>.py`, import in `models/__init__.py`, run `alembic revision --autogenerate`

**New frontend component:** Create `frontend/src/components/<Name>/<Name>.tsx` with named export

**New data-fetching hook:** Add `frontend/src/hooks/use<Resource>.ts` wrapping `useQuery`

**New shared TS type:** Add to `frontend/src/types/index.ts`

**New env var:** Add to `Settings` in `backend/app/config.py` and document in `.env.example`

## Special Directories

**`backend/migrations/versions/`** — Alembic migration scripts (currently empty, initial migration not generated)

**`Lib/`, `Scripts/`, `myenv/`** — Python virtualenv artifacts at repo root (gitignored but physically present — should be outside repo)

**`.planning/`** — GSD planning documents (phases, codebase analysis)

---

*Structure analysis: 2026-03-28*
