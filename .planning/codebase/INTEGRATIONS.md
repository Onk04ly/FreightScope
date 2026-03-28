# External Integrations

**Analysis Date:** 2026-03-28

## APIs & External Services

**AI / ML Inference:**
- **Hugging Face Inference API** — Remote hosted model inference for all AI tasks
  - Base URL: `https://api-inference.huggingface.co/models`
  - Client: `D:/FreightScope/backend/app/services/hf_client.py` (custom async `httpx` wrapper)
  - Auth env var: `HF_API_KEY` (Bearer token, `hf_*` format)
  - Two call modes:
    - `infer(model_id, payload)` — JSON body for text/NER tasks
    - `infer_image(model_id, image_path)` — Binary `application/octet-stream` for image tasks
  - Retry policy: up to 5 attempts, 20s × (attempt+1) backoff on HTTP 503 (model cold-start)
  - Request timeout: 60 seconds
  - Models in use:

    | Model ID | Task | Worker |
    |----------|------|--------|
    | `microsoft/layoutlmv3-base` | Document QA on invoice PDFs | `D:/FreightScope/backend/app/workers/doc_worker.py` |
    | `google/vit-base-patch16-224` | Image classification for cargo damage severity | `D:/FreightScope/backend/app/workers/image_worker.py` |
    | `dslim/bert-base-NER` | Named-entity recognition on carrier notes | `D:/FreightScope/backend/app/workers/ner_worker.py` |
    | `sentence-transformers/all-MiniLM-L6-v2` | Sentence embeddings for entity deduplication | `D:/FreightScope/backend/app/workers/ner_worker.py` |

**Weather Data:**
- **OpenWeatherMap API v2.5** — Current weather at port cities for logistics intelligence
  - Endpoint: `https://api.openweathermap.org/data/2.5/weather`
  - Client: `D:/FreightScope/backend/app/services/weather.py`
  - Auth env var: `OPENWEATHER_API_KEY`
  - Params: `q={city}`, `units=metric`
  - Returns: city, weather description, temperature (°C), wind speed (m/s)
  - Graceful degradation: returns `{}` if key is absent or request fails
  - Request timeout: 10 seconds

**Country / Route Metadata:**
- **REST Countries API v3.1** — Country metadata for trade route enrichment
  - Endpoint: `https://restcountries.com/v3.1/name/{country_name}`
  - Client: `D:/FreightScope/backend/app/services/countries.py`
  - Auth: None (public API)
  - Fields fetched: `name`, `region`, `subregion`, `tld`, `cca2`
  - Graceful degradation: returns `{"name": country_name}` on any error
  - Request timeout: 10 seconds

## Data Storage

**Primary Database:**
- **PostgreSQL 16** (Docker image: `postgres:16-alpine`)
  - Driver: `asyncpg` >=0.29.0
  - ORM: SQLAlchemy >=2.0.0 async engine (`D:/FreightScope/backend/app/database.py`)
  - Session factory: `async_sessionmaker`, injected via `get_db()` FastAPI dependency
  - Migrations: Alembic >=1.13.0 (`D:/FreightScope/backend/migrations/`)
  - Connection env var: `DB_URL`
  - Default DSN: `postgresql+asyncpg://freightscope:freightscope@localhost:5432/freightscope`
  - Docker: port `5432:5432`, persistent named volume `postgres_data`
  - Health check: `pg_isready -U freightscope`

**File Storage:**
- Local filesystem — uploaded documents and images stored under `UPLOAD_DIR`
  - Default path: `uploads/` (relative to backend working directory)
  - Configured via `upload_dir` setting in `D:/FreightScope/backend/app/config.py`
  - No cloud object storage (S3, GCS, Azure Blob) detected

**Caching:**
- None dedicated — Redis is used solely for Celery broker/result purposes, not application-level caching

## Message Queue / Task Infrastructure

**Broker & Result Backend:**
- **Redis 7** (Docker image: `redis:7-alpine`)
  - Single instance serves as both Celery broker and result backend
  - Connection env var: `REDIS_URL`
  - Default: `redis://localhost:6379/0`
  - Docker: port `6379:6379`
  - Health check: `redis-cli ping`

**Task Queue:**
- **Celery >=5.3.0** (`D:/FreightScope/backend/app/workers/celery_app.py`)
  - Broker: Redis
  - Result backend: Redis
  - Serialization: JSON (tasks and results)
  - Timezone: UTC, `enable_utc=True`
  - `task_track_started=True` — task state visible during execution
  - Named queues with direct exchange routing:
    - `doc` → `D:/FreightScope/backend/app/workers/doc_worker.py`
    - `image` → `D:/FreightScope/backend/app/workers/image_worker.py`
    - `ner` → `D:/FreightScope/backend/app/workers/ner_worker.py`

**Task Monitoring:**
- **Flower 2.0** (Docker image: `mher/flower:2.0`)
  - Web UI for Celery task inspection and management
  - Port: `5555:5555`
  - Env: `CELERY_BROKER_URL=redis://redis:6379/0`
  - Depends on Redis service being healthy

## Real-Time Communication

**WebSocket:**
- Native FastAPI WebSocket at `/status/{task_id}` (`D:/FreightScope/backend/app/api/ws.py`)
- Polls Celery `AsyncResult` every 1 second, pushes JSON state updates to client
- Terminates on `SUCCESS`, `FAILURE`, or client disconnect
- Frontend consumes via `D:/FreightScope/frontend/src/hooks/useTaskStatus.ts`
- Vite dev proxy: `/status` → `ws://localhost:8000`

## Authentication & Identity

**API Auth:**
- `SECRET_KEY` env var present in `.env.example` — wired in settings but no auth middleware confirmed in reviewed source files
- No third-party auth provider (Auth0, Clerk, Supabase, etc.) detected
- No JWT or session middleware observed in `D:/FreightScope/backend/app/main.py`

## Monitoring & Observability

**Task Monitoring:**
- Flower 2.0 at `http://localhost:5555` (Docker Compose, development)

**Error Tracking:**
- No dedicated service detected (no Sentry, Datadog, Rollbar, etc.)

**Logging:**
- FastAPI/Uvicorn: default structured logging to stdout
- Alembic: `INFO` level to stderr (`D:/FreightScope/backend/alembic.ini`)
- SQLAlchemy engine: `WARN` level (suppressed in development)
- Celery workers: standard Celery stdout logging

## CI/CD & Deployment

**Container Orchestration:**
- Docker Compose (`D:/FreightScope/docker-compose.yml`) — local/development environment
  - Defines: `postgres`, `redis`, `flower`
  - Backend (FastAPI + Uvicorn) and frontend (Vite) are run outside Docker; not defined as Compose services

**Hosting:**
- No CI/CD pipeline or cloud deployment configuration detected in reviewed files

## Environment Configuration

**Required env vars:**

| Variable              | Purpose                                        | Default / Example                                                   |
|-----------------------|------------------------------------------------|---------------------------------------------------------------------|
| `HF_API_KEY`          | Hugging Face Inference API Bearer token        | `hf_your_token_here`                                                |
| `DB_URL`              | PostgreSQL async connection DSN                | `postgresql+asyncpg://freightscope:freightscope@localhost:5432/freightscope` |
| `REDIS_URL`           | Redis connection URL (broker + result backend) | `redis://localhost:6379/0`                                          |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key                         | `your_openweather_key_here`                                         |
| `SECRET_KEY`          | Application secret for signing                 | `change_me_in_production`                                           |
| `UPLOAD_DIR`          | Local path for uploaded file storage           | `uploads`                                                           |

**Secrets location:**
- `.env` file loaded from backend working directory by pydantic-settings
- Template committed at `D:/FreightScope/.env.example` (no real secrets)
- `.env` must remain untracked by git

## Webhooks & Callbacks

**Incoming:** None detected

**Outgoing:** None detected — all external APIs are synchronous request/response (no webhooks)

---

*Integration audit: 2026-03-28*
