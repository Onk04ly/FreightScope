# Technology Stack

**Analysis Date:** 2026-03-28

## Languages

**Primary:**
- Python 3.x — Backend API, Celery workers, data processing, migrations (`D:/FreightScope/backend/`)
- TypeScript 5.4.5 — Frontend application, strict mode, ES2020 target (`D:/FreightScope/frontend/src/`)

**Secondary:**
- SQL — PostgreSQL schema and queries via SQLAlchemy ORM

## Runtime

**Backend:**
- Python (CPython) — asyncio throughout; targets 3.11+ for `asyncpg` and asyncio compatibility
- ASGI server: Uvicorn >=0.29.0 with `[standard]` extras (WebSocket support)

**Frontend:**
- Browser (ES2020 target, `lib: ["ES2020", "DOM", "DOM.Iterable"]`)
- Node.js — development toolchain only (Vite dev server, TypeScript compiler)

**Package Managers:**
- Backend: pip — `D:/FreightScope/backend/requirements.txt`
- Frontend: npm — `D:/FreightScope/frontend/package.json` (ESM `"type": "module"`)

## Frameworks

**Backend Core:**
- FastAPI >=0.111.0 — Async REST API and WebSocket server (`D:/FreightScope/backend/app/main.py`)
- Uvicorn >=0.29.0 — ASGI server (standard extras for WS)
- Pydantic >=2.7.0 — Data validation and schema definitions
- Pydantic-Settings >=2.2.0 — `.env`-based configuration (`D:/FreightScope/backend/app/config.py`)
- SQLAlchemy[asyncio] >=2.0.0 — Async ORM with `DeclarativeBase` (`D:/FreightScope/backend/app/database.py`)
- Alembic >=1.13.0 — Database schema migrations (`D:/FreightScope/backend/migrations/`)

**Async Task Queue:**
- Celery >=5.3.0 with `[redis]` extra — Background AI inference workers
  - Three named queues: `doc`, `image`, `ner`
  - Config: `D:/FreightScope/backend/app/workers/celery_app.py`

**Frontend Core:**
- React 18.3.1 — UI component framework (`D:/FreightScope/frontend/src/App.tsx`)
- React DOM 18.3.1 — DOM renderer (`D:/FreightScope/frontend/src/main.tsx`)

**Build/Dev:**
- Vite 5.2.0 — Dev server and production bundler (`D:/FreightScope/frontend/vite.config.ts`)
- `@vitejs/plugin-react` 4.2.1 — React JSX transform plugin
- TypeScript compiler (`tsc`) — Type-check step before production build (`tsc && vite build`)

**Testing:**
- pytest >=8.1.0 — Test runner (`D:/FreightScope/backend/tests/`)
- pytest-asyncio >=0.23.0 — Async test support
- anyio >=4.3.0 — Async compatibility layer

## Key Dependencies

**Backend — Database:**
- `asyncpg` >=0.29.0 — Async PostgreSQL driver (required by SQLAlchemy `postgresql+asyncpg://` DSN)
- `redis` >=5.0.0 — Python Redis client (Celery broker + result backend)

**Backend — API / HTTP:**
- `httpx` >=0.27.0 — Async HTTP client for all outbound calls (HF API, OpenWeatherMap, REST Countries)
- `python-multipart` >=0.0.9 — Multipart form/file upload parsing for FastAPI

**Backend — Data / AI:**
- `pandas` >=2.2.0 — Tabular data processing in risk scoring
- `numpy` >=1.26.0 — Numerical operations; z-score anomaly detection in `D:/FreightScope/backend/app/services/risk_scorer.py`
- `pdf2image` >=1.17.0 — PDF-to-image conversion for document worker (requires system Poppler)
- `Pillow` >=10.3.0 — Image handling

**Backend — Config:**
- `python-dotenv` >=1.0.0 — `.env` file loading

**Frontend — State / Data:**
- `@tanstack/react-query` 5.28.0 — Server-state management and async data fetching (`D:/FreightScope/frontend/src/hooks/`)

**Frontend — UI:**
- `recharts` 2.12.2 — Charts and data visualisation
- `leaflet` 1.9.4 — Interactive map library
- `react-leaflet` 4.2.1 — React bindings for Leaflet (`D:/FreightScope/frontend/src/components/MapView/MapView.tsx`)

**Frontend — Dev / Types:**
- `@types/leaflet` 1.9.10
- `@types/react` 18.3.1
- `@types/react-dom` 18.3.0

## Celery Worker Architecture

Three named queues, each with a dedicated worker module:

| Queue   | Worker File                                              | AI Task                        |
|---------|----------------------------------------------------------|--------------------------------|
| `doc`   | `D:/FreightScope/backend/app/workers/doc_worker.py`      | PDF invoice extraction (LayoutLMv3) |
| `image` | `D:/FreightScope/backend/app/workers/image_worker.py`    | Cargo damage classification (ViT) |
| `ner`   | `D:/FreightScope/backend/app/workers/ner_worker.py`      | Named-entity recognition + dedup (BERT + MiniLM) |

Serialization: JSON. Timezone: UTC. `task_track_started=True`.

## Configuration

**Backend Environment:**
- Loaded from `.env` via pydantic-settings (`D:/FreightScope/backend/app/config.py`)
- Template: `D:/FreightScope/.env.example`
- Required vars: `HF_API_KEY`, `DB_URL`, `REDIS_URL`, `OPENWEATHER_API_KEY`, `SECRET_KEY`, `UPLOAD_DIR`

**Frontend Build:**
- `D:/FreightScope/frontend/vite.config.ts` — Dev proxy: `/api` → `http://localhost:8000`, `/status` → `ws://localhost:8000`
- `D:/FreightScope/frontend/tsconfig.json` — Strict TypeScript (`noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`)

**Database Migrations:**
- `D:/FreightScope/backend/alembic.ini` — Script location: `migrations/`, DSN from `sqlalchemy.url`

## Infrastructure / Deployment

**Containerisation:**
- Docker Compose 3.9 — `D:/FreightScope/docker-compose.yml`
  - `postgres:16-alpine` — PostgreSQL 16 (port 5432, persistent volume `postgres_data`)
  - `redis:7-alpine` — Redis 7 (port 6379)
  - `mher/flower:2.0` — Celery task monitoring UI (port 5555)
- FastAPI backend and Vite frontend are **not** defined as Compose services; they run on the host

**Platform Notes:**
- Poppler system dependency required by `pdf2image` for PDF-to-image conversion
- CORS: `http://localhost:5173` allowed (FastAPI CORSMiddleware in `D:/FreightScope/backend/app/main.py`)
- File uploads stored locally under `UPLOAD_DIR` (default: `uploads/`); no cloud object storage

---

*Stack analysis: 2026-03-28*
