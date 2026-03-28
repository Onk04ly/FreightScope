# Codebase Concerns

**Analysis Date:** 2026-03-28

---

## Security

**CORS hardcoded to localhost** | Severity: HIGH
- allow_origins hardcoded in backend/app/main.py
- Fix: Read from settings.CORS_ORIGINS env var

**SECRET_KEY never loaded into Settings** | Severity: HIGH  
- backend/app/config.py has no secret_key field
- Fix: Add secret_key: str with no default

**hf_api_key defaults to empty string** | Severity: HIGH
- Workers fail silently after exhausting retries with empty Bearer token
- Fix: Remove default from backend/app/config.py

**Uploads: no size limit, no MIME validation** | Severity: HIGH
- backend/app/api/upload.py writes any file to disk without checks
- Fix: Enforce MAX_UPLOAD_BYTES, validate content-type allowlist

**Path traversal via file extension** | Severity: MEDIUM
- ext taken from original filename without sanitisation
- Fix: Validate against allowlist (.pdf, .png, .jpg, .jpeg, .txt)

**No auth/authorisation system** | Severity: HIGH
- Any client can read/write all shipment data

**WebSocket /status/{task_id} has no auth** | Severity: MEDIUM
- Files: backend/app/api/ws.py

---

## Placeholder / Stub Logic

**Billing anomaly is hardcoded > 100_000 threshold** | Severity: HIGH
- Explicit placeholder comment in backend/app/workers/doc_worker.py lines 73-80
- Fix: Use zscore_anomaly() against rolling baseline

**fused_score never written to DB -- always NULL** | Severity: HIGH
- compute_fused_score() exists but no worker calls it
- Fix: Call after each worker updates its signal column

**delay_days_p50/p90/forecast never populated** | Severity: HIGH
- Delay forecast chart never renders
- Files: backend/app/models/risk_result.py, backend/app/schemas/risk.py

**Shipment.status stays pending forever** | Severity: MEDIUM
- Workers update RiskResult but never transition status

**incident_summary always NULL** | Severity: MEDIUM
- AI Summary incident never shown in IncidentFeed

**image_worker uses ViT (ImageNet) for damage -- model mismatch** | Severity: MEDIUM
- ImageNet labels have no damage keywords; severity always returns none
- Fix: Replace with CLIP zero-shot classifier

**ner_mismatch signal never set** | Severity: MEDIUM
- ner_worker never compares extracted ORG entities against Shipment.carrier

---

## Tech Debt

**asyncio.get_event_loop().run_until_complete() -- deprecated Python 3.10+** | Severity: HIGH
- All three worker files use this pattern
- Fix: Replace with asyncio.run(...)

**send_task string names missing app. prefix -- tasks never consumed** | Severity: HIGH
- upload.py calls workers.doc_worker.process_invoice but task is app.workers.doc_worker.process_invoice
- All uploads stuck in PENDING forever
- Fix: Use process_invoice.delay(doc.id) or fix string names

**Alembic versions/ empty -- no initial migration** | Severity: MEDIUM
- Fix: alembic revision --autogenerate -m initial

**alembic.ini hardcodes DB URL** | Severity: MEDIUM
- Fix: Override in migrations/env.py via config.set_main_option(...)

**Celery result backend no expiry -- unbounded Redis growth** | Severity: MEDIUM
- Fix: result_expires=3600 in celery_app.conf.update

---

## Performance

**useRiskCard polls every 3s unconditionally** | Severity: MEDIUM
- Fix: refetchInterval: (data) => !data?.fused_score ? 3000 : false

**HF retry blocks Celery worker up to 300s** | Severity: MEDIUM
- Linear backoff 20+40+60+80+100=300s blocking
- Fix: Use Celery self.retry(countdown=...)

**No DB indices on created_at or shipment_id FK** | Severity: MEDIUM
- GET /api/shipments does full scan with ORDER BY
- Fix: Add indices on shipments.created_at and risk_results.shipment_id

**No DB connection pool config -- default 5 may exhaust** | Severity: MEDIUM
- Fix: Set pool_size, max_overflow, pool_timeout in database.py

---

## Observability

**No structured logging anywhere in backend** | Severity: HIGH
- Exceptions swallowed with bare except blocks in all workers
- Fix: logging.getLogger(__name__) in each module

**/health does not probe DB or Redis** | Severity: MEDIUM

**weather.py and countries.py silently return empty dicts** | Severity: MEDIUM
- Fix: Log at WARNING before returning fallback

**No error tracking (Sentry, etc.)** | Severity: MEDIUM

---

## Infrastructure & Scaling

**Uploads on local filesystem -- no horizontal scaling** | Severity: HIGH
- Fix: Replace with S3/GCS/MinIO

**pdf2image requires poppler -- undeclared, uncontainerised** | Severity: HIGH
- Invoice processing broken in any container deployment
- Fix: Add poppler-utils to backend Dockerfile

**No Dockerfile for backend or frontend** | Severity: MEDIUM
- docker-compose.yml only runs infra
- Fix: Add backend/Dockerfile and frontend/Dockerfile

---

## Developer Experience

**vite.config.ts missing proxy -- /api returns 404 in dev** | Severity: MEDIUM
- frontend/src/api/client.ts uses relative /api with no proxy
- Fix: Add server.proxy to vite.config.ts

**useTaskStatus hardcodes WebSocket port 8000** | Severity: MEDIUM
- Files: frontend/src/hooks/useTaskStatus.ts line 4
- Fix: Use VITE_WS_BASE env var

**Two virtualenvs at repo root (Lib/, myenv/)** | Severity: MEDIUM
- Fix: Move outside repo root

**No pyproject.toml/pytest.ini** | Severity: LOW
- Mixed anyio/asyncio markers may cause silent test skips
- Fix: Add pyproject.toml with asyncio_mode

**IncidentFeed uses array index as React key** | Severity: LOW
- Files: frontend/src/components/IncidentFeed/IncidentFeed.tsx line 43
- Fix: Use key={inc.label}

---

*Concerns audit: 2026-03-28*
