# FreightScope Roadmap

**Created:** 2026-03-28
**Milestone:** v1 — End-to-end working pipeline, deployed

---

## Phase 1: Pipeline Activation

**Goal:** A single upload of three files produces a fully populated RiskResult row. Nothing stuck in PENDING.

**Why this first:** The entire project is broken at the task dispatch layer. No other work is verifiable until tasks actually run.

**Requirements:** PIPE-01 through PIPE-07

**Key tasks:**
- Fix `send_task` string names (missing `app.` prefix — all tasks currently stuck in PENDING forever)
- Replace `asyncio.get_event_loop().run_until_complete()` → `asyncio.run()` in all three workers
- Generate initial Alembic migration; fix `alembic.ini` to read DB URL from env
- Add Vite dev proxy to `vite.config.ts` (`/api` → `http://localhost:8000`, `/ws` → `ws://localhost:8000`)
- Fix WebSocket URL in `useTaskStatus.ts` (remove hardcoded port 8000)
- Wire `compute_fused_score()` call after each worker writes its signal columns
- Add Shipment.status transitions in workers (pending → processing → complete)

**Done when:** Upload 3 files, all three workers process, RiskResult row has non-NULL values, fused_score is written.

---

## Phase 2: Model Accuracy & Scoring

**Goal:** Every AI signal returns a meaningful value. No placeholder logic, no wrong models.

**Why second:** The pipeline runs after Phase 1 but returns garbage — wrong model for damage, hardcoded billing threshold, silent NER mismatch. Fix accuracy before adding the 4th signal.

**Requirements:** MODL-01 through MODL-06

**Key tasks:**
- Replace `google/vit-base-patch16-224` with `openai/clip-vit-base-patch32` zero-shot in `image_worker.py`
  - Candidate labels: `["no damage", "minor damage", "moderate damage", "severe damage"]`
  - Map top label → severity enum
- Fix billing anomaly: call `zscore_anomaly()` from `risk_scorer.py` against rolling invoice total baseline
- Wire `ner_mismatch`: after NER runs, compare extracted ORG entities against `Shipment.carrier` (case-insensitive substring match)
- Generate `incident_summary`: template-driven string summarizing top 2–3 risk signals by severity
- Fix Celery `self.retry(countdown=30, max_retries=3)` in all workers (currently structural but never triggered)
- Set `result_expires=3600` in `celery_app.conf.update`

**Done when:** Damage photo returns a severity score that maps to a real category, billing anomaly flags based on statistics, NER mismatch fires on carrier name discrepancy, incident_summary is non-NULL.

---

## Phase 3: Delay Forecast

**Goal:** Fourth AI signal — route delay probability with p50/p90 estimates and a 7-day forecast curve.

**Why third:** Adds the final signal before dashboard polish. Dataset research gates everything else in this phase.

**Requirements:** DLAY-01 through DLAY-06

**Key tasks:**
- Research and select real public freight delay dataset (candidates: BTS T-100, Kaggle "Supply Chain" or "Shipping Dataset")
- Document dataset source, license, and field mapping in `backend/data/README.md`
- Pre-process dataset into a route → delay lookup table (origin region, destination region, carrier type → historical delay distribution)
- Build `delay_worker.py`: reads Shipment route metadata (from NER-extracted LOC entities + carrier), queries lookup, runs regression or percentile calculation
- Add `delay` queue to `celery_app.py` and dispatch from `upload.py`
- Populate `delay_days_p50`, `delay_days_p90`, `delay_forecast` JSONB (array of `{day, probability}` objects for Recharts)
- Update `compute_fused_score()` to incorporate delay signal
- Verify Recharts delay chart in frontend renders the populated data

**Done when:** Every shipment gets a delay forecast, `delay_forecast` JSONB is populated, chart renders 7-day curve, fused_score incorporates delay.

---

## Phase 4: Dashboard Completion

**Goal:** The dashboard tells the complete story. All four signals visible, UX complete, no dead UI states.

**Why fourth:** All signals exist after Phase 3. Now connect them to the UI and polish the experience.

**Requirements:** DASH-01 through DASH-06

**Key tasks:**
- `RiskCard`: verify fused score dial, damage severity indicator, billing anomaly bar all render with real data
- `IncidentFeed`: derive incident entries from all four signals (damage severity, billing anomaly, ner_mismatch, delay p90)
- `IncidentFeed`: render `incident_summary` as top-of-feed AI summary card
- Shipment list: show correct status badges (pending / processing / complete) from `Shipment.status`
- `useRiskCard`: change `refetchInterval` to `(data) => !data?.fused_score ? 3000 : false` — stop polling when complete
- `MapView`: render route markers from extracted LOC entities in NER results (origin → destination)
- Fix React key prop on `IncidentFeed` items (use label, not array index)

**Done when:** End-to-end demo path — upload, watch progress, see complete risk card — works without dead panels or NULL values.

---

## Phase 5: Security & Hardening

**Goal:** Production-safe code. No critical security holes, proper logging, DB performance baselines.

**Why fifth:** Security and performance concerns are known but don't block demos. Fix before going live.

**Requirements:** HARD-01 through HARD-07

**Key tasks:**
- `upload.py`: validate MIME type (`application/pdf`, `image/png`, `image/jpeg`, `text/plain`), extension allowlist, max 10MB per file
- `upload.py`: sanitize file extension — derive from MIME type, not original filename
- `config.py`: move `CORS_ORIGINS` to Settings, remove hardcoded `http://localhost:5173` from `main.py`
- `config.py`: remove default empty string from `hf_api_key`; fail fast on startup if missing
- Add `logging.getLogger(__name__)` to all backend modules and workers; replace bare `except` blocks with logged exceptions
- `/health`: probe `asyncpg` connection and Redis ping; return 503 if either fails
- Alembic migration: add indices on `shipments.created_at` and `risk_results.shipment_id`
- `database.py`: set `pool_size=10`, `max_overflow=20`, `pool_timeout=30`

**Done when:** Upload validation rejects bad files with clear errors, server won't start without HF API key, all exceptions are logged, `/health` returns real status.

---

## Phase 6: Deployment

**Goal:** One `docker-compose up` starts the full stack. Live URL deployed for portfolio.

**Why last:** All code must be correct before containerizing. Deployment reveals final env/config gaps.

**Requirements:** DEPL-01 through DEPL-05

**Key tasks:**
- `backend/Dockerfile`: Python 3.11-slim, install `poppler-utils` via apt, copy app, expose 8000
- `frontend/Dockerfile`: Node 20-alpine build stage, Nginx serve stage
- `docker-compose.yml`: add `backend`, `celery-worker`, and `frontend` services with health checks and env file
- Production `CORS_ORIGINS` set to deployed frontend URL
- `UPLOAD_DIR` mounted as named volume in compose
- Choose hosting platform (Railway recommended for simplicity), configure env vars
- Add `seed_demo.py` script: creates one sample shipment + documents on first run for portfolio demo
- Write `README.md` deployment section (start command, required env vars, first-run instructions)

**Done when:** `docker-compose up` starts all services, `seed_demo.py` creates a demo shipment, live URL returns the dashboard with a pre-processed risk card.

---

## Summary

| Phase | Name | Requirements | Status |
|-------|------|-------------|--------|
| 1 | Pipeline Activation | PIPE-01–07 | Pending |
| 2 | Model Accuracy & Scoring | MODL-01–06 | Pending |
| 3 | Delay Forecast | DLAY-01–06 | Pending |
| 4 | Dashboard Completion | DASH-01–06 | Pending |
| 5 | Security & Hardening | HARD-01–07 | Pending |
| 6 | Deployment | DEPL-01–05 | Pending |

**Total v1 requirements:** 37
**Total phases:** 6

---
*Roadmap created: 2026-03-28*
