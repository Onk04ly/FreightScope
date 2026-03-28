# Architecture

**Analysis Date:** 2026-03-28

## Pattern Overview

**Overall:** Dual-process monorepo — a single FastAPI backend paired with a React SPA frontend, connected by REST and WebSocket. Background AI inference runs in Celery workers decoupled from the request cycle via Redis as broker/backend. There are no microservices; all backend Python code shares one module tree.

**Key Characteristics:**
- Async-first backend (asyncpg, SQLAlchemy async, httpx async) with synchronous Celery workers that bridge into async via `asyncio.get_event_loop().run_until_complete()`
- Three independent Celery task queues — `doc`, `image`, `ner` — one per AI modality
- Frontend polls REST endpoints with React Query for state refresh; uses raw WebSocket for real-time task progress
- No authentication layer is present in the current codebase

---

## Layers

**API Layer:**
- Purpose: Receive HTTP requests, validate input, dispatch Celery tasks, return responses
- Location: `backend/app/api/`
- Contains: FastAPI `APIRouter` modules — `upload.py`, `shipments.py`, `risk.py`, `ws.py`
- Depends on: `app/database.py` (session), `app/models/`, `app/schemas/`, `app/workers/celery_app.py`
- Used by: Frontend via HTTP/WebSocket through Vite dev proxy

**Schema Layer:**
- Purpose: Request/response validation and serialization via Pydantic v2
- Location: `backend/app/schemas/`
- Contains: `upload.py` (UploadResponse), `shipment.py` (ShipmentRead), `risk.py` (RiskCard, DelayForecastDay)
- Depends on: Pydantic BaseModel, references `app/models/shipment.py` enums
- Used by: API layer as `response_model=` annotations

**ORM / Model Layer:**
- Purpose: SQLAlchemy declarative models mapping to PostgreSQL tables
- Location: `backend/app/models/`
- Contains: `shipment.py` (Shipment, ShipmentStatus enum), `document.py` (Document, DocType enum), `risk_result.py` (RiskResult with JSONB fields)
- Depends on: `app/database.py` (Base, engine)
- Used by: API layer and Celery workers both query models directly

**Database Access:**
- Purpose: Async SQLAlchemy engine and session factory; SQLDeclarativeBase definition
- Location: `backend/app/database.py`
- Pattern: Dependency injection via `get_db()` async generator for API routes; `AsyncSessionLocal` context manager used directly in workers
- Used by: API layer (via `Depends(get_db)`), all Celery workers

**Services Layer:**
- Purpose: Stateless utility functions for external calls and scoring logic
- Location: `backend/app/services/`
- Contains:
  - `hf_client.py` — httpx async client for HF Inference API (text and image variants, auto-retry on 503)
  - `risk_scorer.py` — pure NumPy/Pandas fused score computation (`compute_fused_score`, `zscore_anomaly`)
  - `weather.py` — httpx async client for OpenWeatherMap current weather
  - `countries.py` — httpx async client for REST Countries API
- Depends on: `app/config.py` (API keys), `httpx`, `numpy`
- Used by: Celery workers (`hf_client`); `risk_scorer` is available but not yet wired to any automated scoring trigger

**Worker Layer:**
- Purpose: Run AI inference tasks off the request path; write results back to PostgreSQL
- Location: `backend/app/workers/`
- Contains:
  - `celery_app.py` — Celery instance, Redis broker/backend, three named queues
  - `doc_worker.py` — invoice PDF → LayoutLMv3-base Document QA → billing anomaly flag
  - `image_worker.py` — cargo image → ViT-base-patch16-224 classification → damage severity
  - `ner_worker.py` — carrier note text → bert-base-NER entities → all-MiniLM-L6-v2 dedup → grouped entities
- Depends on: `app/services/hf_client.py`, `app/database.py`, `app/models/`
- Used by: Dispatched via `celery_app.send_task()` from `api/upload.py`

**Configuration:**
- Purpose: Typed settings loaded from `.env` via pydantic-settings
- Location: `backend/app/config.py`
- Singleton: `settings = Settings()` imported throughout the backend

---

## Data Flow

**Shipment Upload Flow:**

1. Frontend `UploadZone` POSTs multipart form to `POST /api/upload`
2. `upload.py` router creates `Shipment` and empty `RiskResult` rows in PostgreSQL
3. For each uploaded file, a `Document` row is written and a Celery task dispatched to the matching queue (`doc`, `image`, or `ner`)
4. API immediately returns `{shipment_id, task_ids, message}` — no waiting for inference
5. Celery worker picks up the task, calls HF Inference API via `hf_client.py`, writes results back to `risk_results` table
6. Frontend `useTaskStatus` hook opens a WebSocket to `ws://…/status/{task_id}` and polls Celery task state every 1 second
7. WebSocket closes automatically on `SUCCESS` or `FAILURE`

**Risk Card Polling Flow:**

1. `RiskCard` and `IncidentFeed` components both call `useRiskCard(shipmentId)` which wraps `GET /api/risk/{shipment_id}`
2. React Query refetches every 3 seconds until risk data populates
3. `RiskCard` renders fused score dial, delay forecast line chart (Recharts), and billing anomaly bar
4. `IncidentFeed` derives incident entries from the same `RiskCard` data (no separate endpoint)

**Shipment List Polling Flow:**

1. `useShipments` wraps `GET /api/shipments?skip=0&limit=20`
2. React Query refetches every 5 seconds
3. App renders clickable shipment list in left sidebar; selection drives `selectedShipment` state

**State Management:**

- All server state is managed by TanStack React Query (v5) with `staleTime: 2000ms`
- Local UI state (selected shipment, form fields, task ID) is plain `useState` in `App.tsx` and `UploadZone`
- No global state store (no Redux, Zustand, or Context)

---

## Key Abstractions

**RiskResult:**
- Purpose: Aggregates all AI-derived signals for a shipment into one row
- Location: `backend/app/models/risk_result.py`, `backend/app/schemas/risk.py`
- Pattern: One-to-one with Shipment (unique FK, cascade delete); fields start null and are written by workers as they complete; JSONB used for `ner_entities` and `delay_forecast`

**Celery Task:**
- Purpose: Unit of async AI inference work, identified by UUID task ID
- Pattern: Tasks are dispatched with `celery_app.send_task(name, args=[document_id], queue=...)`. Each worker reads the Document, calls HF, and updates RiskResult. Task IDs are returned to the frontend for WebSocket progress tracking.

**HF Inference Client:**
- Purpose: Thin async wrapper around HF Inference API with 503 retry logic
- Location: `backend/app/services/hf_client.py`
- Pattern: Two functions — `infer(model_id, payload)` for JSON/text models, `infer_image(model_id, image_path)` for binary image upload. Up to 5 retries with 20s * attempt backoff.

**Document:**
- Purpose: Tracks uploaded files and their processing state
- Location: `backend/app/models/document.py`
- Pattern: Enum `DocType` (`invoice`, `image`, `note`) determines which worker processes it. `processed_at` is set by the worker on completion.

---

## Entry Points

**Backend API Server:**
- Location: `backend/app/main.py`
- Triggers: `uvicorn app.main:app --reload` (development)
- Responsibilities: Mounts CORS middleware (allows `http://localhost:5173`), registers four routers under `/api`, creates upload dir on startup, exposes `GET /health`

**Celery Worker Process:**
- Location: `backend/app/workers/celery_app.py`
- Triggers: `celery -A app.workers.celery_app worker -Q doc,image,ner`
- Responsibilities: Consumes tasks from Redis queues; each worker module registered in `include=[]`

**Frontend Dev Server:**
- Location: `frontend/src/main.tsx`
- Triggers: `npm run dev` (Vite on port 5173)
- Responsibilities: Mounts React app with QueryClientProvider; Vite proxy routes `/api` → `http://localhost:8000` and `/status` → `ws://localhost:8000`

---

## Communication Patterns

**REST (HTTP):**
- `POST /api/upload` — multipart form upload, returns task IDs
- `GET /api/shipments` — paginated shipment list
- `GET /api/risk/{shipment_id}` — risk card for a shipment
- `GET /health` — health check

**WebSocket:**
- `WS /status/{task_id}` — server polls Celery AsyncResult every 1s and streams JSON state to client; closes on terminal state
- Client-side: `useTaskStatus` hook in `frontend/src/hooks/useTaskStatus.ts` connects to `ws://{hostname}:8000/status/{task_id}`
- Note: WebSocket connects directly to port 8000 (not through Vite proxy) using `window.location.hostname`

**Task Queue (Redis):**
- Celery uses Redis as both broker and result backend (`redis://localhost:6379/0`)
- Three named queues with dedicated exchanges: `doc`, `image`, `ner`
- Task serialization: JSON

**External HTTP (Backend → External APIs):**
- HF Inference API: `https://api-inference.huggingface.co/models/{model_id}` (POST, Bearer token)
- OpenWeatherMap: `https://api.openweathermap.org/data/2.5/weather` (GET, API key param)
- REST Countries: `https://restcountries.com/v3.1/name/{country}` (GET, no auth)

---

## Error Handling

**Strategy:** Fail-and-log at each layer boundary; no global error middleware beyond FastAPI defaults.

**Patterns:**
- HF client retries on HTTP 503 up to 5 times; raises `RuntimeError` on exhaustion; workers catch per-question errors with bare `except Exception: continue`
- Weather and countries clients return empty dict on any exception (silent degradation)
- Celery tasks have `max_retries=3` and `bind=True` but no explicit `self.retry()` call is present — retries are structural but not triggered
- API routes raise `HTTPException(404)` when RiskResult not found; all other errors propagate as 500
- Frontend `api/client.ts` throws `Error` on non-2xx response; `UploadZone` catches and displays inline

---

## Auth / Security Architecture

**Current state:** No authentication or authorization is implemented. All API endpoints are publicly accessible.

**CORS:** Configured to allow only `http://localhost:5173` (Vite dev server). Production origins are not configured.

**Secrets:** API keys (`HF_API_KEY`, `OPENWEATHER_API_KEY`) and DB credentials are loaded from `.env` via pydantic-settings. A `SECRET_KEY` env var exists in `.env.example` but is not consumed by any middleware.

**File uploads:** Saved to local filesystem under `uploads/` with UUID-prefixed filenames. No file type validation beyond the `accept=` attribute on the frontend form inputs.

---

*Architecture analysis: 2026-03-28*
