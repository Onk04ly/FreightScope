# Coding Conventions

**Analysis Date:** 2026-03-28

---

## Backend (Python / FastAPI)

### Naming Patterns

**Files:**
- Modules use `snake_case`: `risk_scorer.py`, `hf_client.py`, `doc_worker.py`
- Worker files suffixed with `_worker`: `doc_worker.py`, `image_worker.py`, `ner_worker.py`
- Service files suffixed by domain: `hf_client.py`, `weather.py`, `countries.py`, `risk_scorer.py`

**Classes:**
- PascalCase for all classes: `Shipment`, `RiskResult`, `Document`, `ShipmentRead`, `RiskCard`
- SQLAlchemy models: plain noun names (`Shipment`, `Document`, `RiskResult`)
- Pydantic schemas: noun + purpose suffix (`ShipmentRead`, `RiskCard`, `UploadResponse`)
- Enums: PascalCase class, lowercase members (`ShipmentStatus.pending`, `DocType.invoice`)
- Dataclasses: PascalCase (`RiskSignals`)
- Settings: `Settings` with a module-level singleton `settings`

**Functions:**
- `snake_case` throughout: `compute_fused_score`, `get_risk_card`, `list_shipments`
- Private async helpers prefixed with underscore: `_process_invoice`, `_classify_cargo`, `_extract_entities`, `_save`
- Private helpers not meant for export also prefixed with underscore: `_pdf_to_base64_pages`, `_map_label_to_severity`, `_cosine_sim`, `_dedup_entities`
- FastAPI route handlers use verb-noun format: `upload_shipment`, `list_shipments`, `get_risk_card`, `task_status`

**Variables and constants:**
- `snake_case` for variables: `task_ids`, `upload_path`, `billing_anomaly`
- `UPPER_SNAKE_CASE` for module-level constants: `MODEL_ID`, `HF_API_BASE`, `_MAX_RETRIES`, `_RETRY_SLEEP`, `_DELAY_CAP_DAYS`, `_COSINE_DEDUP_THRESHOLD`
- Private module constants prefixed with underscore: `_QUESTIONS`, `_SEVERITY_KEYWORDS`, `_DAMAGE_WEIGHTS`

**Database tables:**
- Plural snake_case: `shipments`, `risk_results`, `documents`

### Code Style

**Formatting:**
- No formatter (Black, ruff, or isort) configured — no `pyproject.toml`, `setup.cfg`, or `.flake8` present
- Code in practice follows PEP 8 style consistently
- Line length appears to follow 100-character soft limit (see `upload.py` line 92)
- Double-quoted strings are standard throughout

**Linting:**
- No linting tool configured
- One `# noqa: F401` comment used in `backend/migrations/env.py` line 9 for a necessary side-effect import

**Python version:**
- Uses modern Python 3.10+ syntax: `str | None` union types, `list[str]` lowercase generics, `dict[str, Any]` without `from __future__ import annotations`

### Import Organization

**Order (observed):**
1. Standard library (`os`, `uuid`, `asyncio`, `json`, `enum`, `datetime`, `dataclasses`, `math`, `io`, `pathlib`)
2. Third-party packages (`fastapi`, `sqlalchemy`, `pydantic`, `celery`, `httpx`, `numpy`)
3. Local application imports (`from app.config import settings`, `from app.database import ...`, `from app.models...`, `from app.services...`, `from app.workers...`)

**Pattern:**
- Always absolute imports: `from app.api import risk, shipments` not relative `from . import`
- Lazy imports inside functions for heavy optional deps: `from pdf2image import convert_from_path` inside `_pdf_to_base64_pages`; `import io` inside a loop in `doc_worker.py`

### Module-level docstrings

Present on worker and service files; absent on model, schema, and API route files:
- `backend/app/services/risk_scorer.py` — has docstring
- `backend/app/workers/doc_worker.py`, `image_worker.py`, `ner_worker.py` — all have docstrings
- `backend/app/services/weather.py`, `countries.py` — have one-line docstrings
- `backend/app/api/*.py`, `backend/app/models/*.py`, `backend/app/schemas/*.py` — no module docstring

### Error Handling Patterns

**API layer:**
- Use `HTTPException` for user-facing errors: `raise HTTPException(status_code=404, detail="Risk result not found")` in `backend/app/api/risk.py`
- No custom exception classes — standard `HTTPException` only

**Service layer:**
- External HTTP calls use bare `except Exception: return {}` / `except Exception: continue` — swallows errors silently and returns safe defaults
- `hf_client.py` raises `RuntimeError` after exhausting retries: `raise RuntimeError(f"HF model {model_id} unavailable after {_MAX_RETRIES} retries")`
- Worker tasks use `try/except Exception: continue` per-question within loops to skip individual failures without aborting the task

**Workers:**
- Celery tasks decorated with `max_retries=3` but explicit retry calls are not present — relies on Celery default retry on unhandled exception
- Async worker logic lives in private `async def _<task_name>` functions; the public `@celery_app.task` function calls `asyncio.get_event_loop().run_until_complete(...)`

### API Design Patterns

**Router organisation:**
- Each domain has its own `APIRouter` in `backend/app/api/`: `shipments.py`, `risk.py`, `upload.py`, `ws.py`
- All HTTP routers registered with `prefix="/api"` in `backend/app/main.py`
- WebSocket router registered without prefix
- Routers use `tags=[...]` for grouping in OpenAPI docs

**Route naming:**
- REST resource paths: `/api/shipments` (collection), `/api/risk/{shipment_id}` (resource by ID)
- Action endpoints: `/api/upload` (POST, verb-as-path for multi-file form)
- WebSocket: `/status/{task_id}`

**Response shapes:**
- List endpoints return bare arrays: `list[ShipmentRead]`
- Single resource returns the schema directly: `RiskCard`
- Create/action endpoints return a dedicated response schema: `UploadResponse`
- Error responses use FastAPI default `{"detail": "..."}` shape via `HTTPException`
- `GET /health` returns `{"status": "ok"}`

**Request validation:**
- Query parameters use `Query(default, ge=..., le=...)` for bounds: `skip: int = Query(0, ge=0)`, `limit: int = Query(20, ge=1, le=100)`
- Form fields validated by presence/type; optional files typed as `UploadFile | None = File(None)`

**Database access:**
- `AsyncSession` via `Depends(get_db)` in route functions
- Raw `select()` statements, not ORM convenience methods: `await db.execute(select(Model).where(...))`
- Flush before commit when inserting related records to get generated IDs: `await db.flush()` after each `db.add()`

**Pydantic schemas:**
- All read schemas set `model_config = {"from_attributes": True}` for ORM ↔ schema conversion
- Schemas live in `backend/app/schemas/` separate from SQLAlchemy models in `backend/app/models/`
- Nullable fields typed as `X | None` (Python 3.10+ style)

---

## Frontend (TypeScript / React)

### Naming Patterns

**Files:**
- Components: PascalCase directory + matching filename: `RiskCard/RiskCard.tsx`, `MapView/MapView.tsx`, `UploadZone/UploadZone.tsx`, `IncidentFeed/IncidentFeed.tsx`
- Hooks: camelCase with `use` prefix: `useShipments.ts`, `useRiskCard.ts`, `useTaskStatus.ts`
- API client: `client.ts` in `src/api/`
- Types barrel: `src/types/index.ts`

**Components:**
- Named exports (not default): `export function RiskCard(...)`, `export function MapView(...)`
- `App.tsx` uses default export: `export default function App()`
- Props interface named `Props` (local to file, not exported): `interface Props { shipmentId: number }`

**Types and interfaces:**
- `interface` for object shapes: `interface Shipment`, `interface RiskCard`, `interface TaskStatus`
- `type` for unions and aliases: `type ShipmentStatus = "pending" | ...`, `type TaskState = "PENDING" | ...`
- All types centralised in `src/types/index.ts` and exported from there

**Variables and constants:**
- `camelCase` for variables and function parameters
- `UPPER_SNAKE_CASE` for module-level lookup tables and constants: `PORT_COORDS`, `SEVERITY_COLOR`, `SEVERITY_BADGE`, `WS_BASE`
- React state setters follow `set<StateName>` convention: `setSelectedShipment`, `setTaskId`, `setError`

**Hooks:**
- All hooks follow `use<Domain>` naming: `useShipments`, `useRiskCard`, `useTaskStatus`
- Hooks in `src/hooks/`, one hook per file

### Code Style

**Formatting:**
- No Prettier or ESLint config files present
- Code uses 2-space indentation consistently
- Double-quoted strings in JSX/TSX attributes; template literals for dynamic strings

**TypeScript strictness (from `tsconfig.json`):**
- `"strict": true` — all strict checks enabled
- `"noUnusedLocals": true`
- `"noUnusedParameters": true`
- `"noFallthroughCasesInSwitch": true`
- `"target": "ES2020"`, `"module": "ESNext"`
- No path aliases configured

### Import Organisation

**Order (observed):**
1. Third-party library imports: `import { useQuery } from "@tanstack/react-query"`
2. Local relative imports: `import { api } from "../api/client"`, `import type { Shipment } from "../../types"`

**Type imports:**
- Use `import type` for type-only imports: `import type { Shipment } from "../../types"`, `import type { RiskCard, Shipment, UploadResponse } from "../types"`

**No barrel re-exports** from component directories — each component imported by full path.

### Component Structure

Components follow this consistent layout:
1. Module-level constants (lookup objects, color maps): `const SEVERITY_COLOR = {...}`
2. Helper functions: `function scoreColor(score: number | null): string {...}`
3. Props interface definition: `interface Props { ... }`
4. Named export function component: `export function ComponentName({ prop }: Props) { ... }`

**Styling approach:**
- All styles written as inline `style` objects — no CSS modules, no Tailwind, no external CSS (except `leaflet/dist/leaflet.css`)
- Style objects sometimes extracted to a named variable for reuse within a file: `const inputStyle: React.CSSProperties = {...}`
- Colors hardcoded as hex literals within components; no shared design token file

### Hooks and State Management

**Data fetching:**
- TanStack Query (`@tanstack/react-query`) for all server state
- `QueryClient` configured in `src/main.tsx` with `staleTime: 2000`, `retry: 1`
- Each data domain has a dedicated hook: `useShipments`, `useRiskCard`
- Polling via `refetchInterval`: `useShipments` refetches every 5000 ms, `useRiskCard` every 3000 ms

**Local state:**
- `useState` for UI state in components: form fields, selected item, error messages, loading flags
- No global state library (Redux, Zustand, Jotai) — state passed down as props from `App.tsx`

**Real-time updates:**
- `useTaskStatus` manages a WebSocket connection using `useEffect` with cleanup:
  ```typescript
  const ws = new WebSocket(`${WS_BASE}/status/${taskId}`);
  ws.onmessage = (event) => { ... };
  ws.onerror = () => ws.close();
  return () => { if (ws.readyState === WebSocket.OPEN) ws.close(); };
  ```
- WebSocket auto-closes on `SUCCESS` or `FAILURE` state

### Error Handling (Frontend)

**In hooks:**
- TanStack Query handles fetch errors internally; components check `isLoading` and `!data` guards

**In event handlers:**
- `try/catch` in async form submit handlers; error stored in local state and rendered inline:
  ```typescript
  setError(err instanceof Error ? err.message : "Upload failed")
  ```

**API client:**
- `client.ts` throws `Error` with status + body text on non-OK responses:
  ```typescript
  throw new Error(`${res.status} ${res.statusText}: ${text}`)
  ```

---

## Cross-Cutting Conventions

**Timestamps:**
- Backend stores and returns UTC timestamps (`DateTime(timezone=True)`, `server_default=func.now()`, `datetime.now(timezone.utc)`)
- Frontend types `created_at` and date fields as `string` (ISO 8601 from JSON)
- Celery configured with `timezone="UTC"`, `enable_utc=True`

**IDs:**
- All database primary keys are auto-increment integers (`Mapped[int] = mapped_column(primary_key=True)`)
- File uploads assigned UUID filenames: `uuid.uuid4()` + original extension

**Enums:**
- Python: `class X(str, enum.Enum)` pattern used for both `ShipmentStatus` and `DocType` — string enums stored in PostgreSQL as enum columns
- TypeScript: string literal union types mirror backend enums: `type ShipmentStatus = "pending" | "processing" | "complete" | "failed"`

**Configuration:**
- Backend config via `pydantic_settings.BaseSettings` reading from `.env` file — single `settings` singleton imported where needed
- Frontend config hard-coded in source: `const BASE = "/api"`, `const WS_BASE = \`ws://...\``; Vite proxy handles dev-time routing

---

*Convention analysis: 2026-03-28*
