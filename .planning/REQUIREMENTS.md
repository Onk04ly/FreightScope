# Requirements: FreightScope

**Defined:** 2026-03-28
**Core Value:** Upload three raw logistics documents → get a fully analyzed risk card in under 40 seconds, no human intervention.

---

## v1 Requirements

### Pipeline (End-to-End Activation)

- [ ] **PIPE-01**: Uploading an invoice PDF, damage photo, and carrier note creates a Shipment and dispatches all three workers
- [ ] **PIPE-02**: All three Celery workers consume their tasks (no tasks stuck in PENDING)
- [ ] **PIPE-03**: Each worker writes its result columns to RiskResult on completion
- [ ] **PIPE-04**: `fused_score` is computed and written to DB after each worker updates its signal
- [ ] **PIPE-05**: Shipment.status transitions from `pending` → `processing` → `complete` as workers run
- [ ] **PIPE-06**: Risk card is fully populated in under 40 seconds from upload
- [ ] **PIPE-07**: Vite dev proxy routes `/api` and `/ws` correctly so frontend connects without manual config

### Model Accuracy

- [ ] **MODL-01**: Cargo damage severity uses CLIP zero-shot classification (not ViT ImageNet labels)
- [ ] **MODL-02**: CLIP returns one of four meaningful severity values: none, minor, moderate, severe
- [ ] **MODL-03**: Billing anomaly is flagged using z-score against a rolling baseline (not hardcoded threshold)
- [ ] **MODL-04**: `ner_mismatch` is set when extracted ORG entities don't match Shipment.carrier
- [ ] **MODL-05**: `incident_summary` is generated and written — a human-readable summary of top risk signals
- [ ] **MODL-06**: Celery workers use `asyncio.run()` instead of deprecated `get_event_loop()`

### Delay Forecast

- [ ] **DLAY-01**: A real public freight delay dataset is selected, documented, and seeded into the system
- [ ] **DLAY-02**: A delay prediction model/lookup produces p50 and p90 delay estimates for a given route
- [ ] **DLAY-03**: A fourth Celery worker (`delay` queue) runs delay forecast on each shipment
- [ ] **DLAY-04**: `delay_days_p50`, `delay_days_p90`, and `delay_forecast` JSONB are populated
- [ ] **DLAY-05**: Delay forecast is factored into `fused_score` computation
- [ ] **DLAY-06**: Frontend delay chart (Recharts) renders real forecast data

### Dashboard Completion

- [ ] **DASH-01**: Risk card displays fused score, damage severity, billing anomaly, and delay forecast
- [ ] **DASH-02**: IncidentFeed shows incident entries derived from all four AI signals
- [ ] **DASH-03**: `incident_summary` is visible in the IncidentFeed
- [ ] **DASH-04**: Shipment list shows correct status badges (pending / processing / complete)
- [ ] **DASH-05**: Risk card polling stops once data is fully populated (no unconditional 3s refetch)
- [ ] **DASH-06**: MapView renders route from extracted LOC entities in carrier note

### Security & Hardening

- [ ] **HARD-01**: File uploads validate MIME type, extension allowlist (.pdf, .png, .jpg, .jpeg, .txt), and max size
- [ ] **HARD-02**: File extension is sanitized against an allowlist (no path traversal via filename)
- [ ] **HARD-03**: CORS origins are read from `settings.CORS_ORIGINS` env var, not hardcoded
- [ ] **HARD-04**: `HF_API_KEY` has no default value — server fails fast with a clear error if missing
- [ ] **HARD-05**: Structured logging is present in all backend modules and workers
- [ ] **HARD-06**: `/health` endpoint probes DB and Redis connectivity (not just HTTP 200)
- [ ] **HARD-07**: DB indices exist on `shipments.created_at` and `risk_results.shipment_id`

### Deployment

- [ ] **DEPL-01**: `backend/Dockerfile` builds the FastAPI app including Poppler system dependency
- [ ] **DEPL-02**: `frontend/Dockerfile` builds the Vite production bundle
- [ ] **DEPL-03**: `docker-compose.yml` includes backend, frontend, Celery worker, postgres, redis, and flower
- [ ] **DEPL-04**: Project deploys successfully to Railway (or Render/Fly.io) with env vars configured
- [ ] **DEPL-05**: A demo shipment is seeded on first startup so the portfolio demo works without manual uploads

---

## v2 Requirements

### Authentication

- **AUTH-01**: Users can log in with email and password
- **AUTH-02**: API endpoints are protected by JWT authentication
- **AUTH-03**: Shipment data is scoped to authenticated user/tenant

### Integrations

- **INTG-01**: Outbound webhook when risk score exceeds threshold
- **INTG-02**: Export risk card as PDF report
- **INTG-03**: Slack notification for high-severity shipments

### Advanced Analytics

- **ANLX-01**: Historical trend view across all shipments
- **ANLX-02**: Carrier performance scorecards
- **ANLX-03**: Route risk heatmap

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| User authentication (v1) | Adds complexity without adding portfolio signal — v2 item |
| Mobile app | Web-first, mobile is a different product |
| Real-time carrier tracking APIs | Requires paid data subscriptions |
| Enterprise TMS integrations | Out of scale for portfolio project |
| Video upload | No use case in logistics document intake |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | Phase 1 | Pending |
| PIPE-02 | Phase 1 | Pending |
| PIPE-03 | Phase 1 | Pending |
| PIPE-04 | Phase 1 | Pending |
| PIPE-05 | Phase 1 | Pending |
| PIPE-06 | Phase 1 | Pending |
| PIPE-07 | Phase 1 | Pending |
| MODL-01 | Phase 2 | Pending |
| MODL-02 | Phase 2 | Pending |
| MODL-03 | Phase 2 | Pending |
| MODL-04 | Phase 2 | Pending |
| MODL-05 | Phase 2 | Pending |
| MODL-06 | Phase 2 | Pending |
| DLAY-01 | Phase 3 | Pending |
| DLAY-02 | Phase 3 | Pending |
| DLAY-03 | Phase 3 | Pending |
| DLAY-04 | Phase 3 | Pending |
| DLAY-05 | Phase 3 | Pending |
| DLAY-06 | Phase 3 | Pending |
| DASH-01 | Phase 4 | Pending |
| DASH-02 | Phase 4 | Pending |
| DASH-03 | Phase 4 | Pending |
| DASH-04 | Phase 4 | Pending |
| DASH-05 | Phase 4 | Pending |
| DASH-06 | Phase 4 | Pending |
| HARD-01 | Phase 5 | Pending |
| HARD-02 | Phase 5 | Pending |
| HARD-03 | Phase 5 | Pending |
| HARD-04 | Phase 5 | Pending |
| HARD-05 | Phase 5 | Pending |
| HARD-06 | Phase 5 | Pending |
| HARD-07 | Phase 5 | Pending |
| DEPL-01 | Phase 6 | Pending |
| DEPL-02 | Phase 6 | Pending |
| DEPL-03 | Phase 6 | Pending |
| DEPL-04 | Phase 6 | Pending |
| DEPL-05 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 37 total
- Mapped to phases: 37
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after initial definition*
