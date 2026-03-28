# FreightScope

**Created:** 2026-03-28
**Type:** Brownfield — significant skeleton exists, not yet end-to-end functional
**Status:** Active development

---

## What It Is

FreightScope is a multimodal AI platform that automates freight document intake. It ingests three document types simultaneously — a PDF invoice, a cargo damage photo, and a plain-text carrier note — runs them through a pipeline of four specialized AI models, and delivers a unified risk card per shipment in under 40 seconds.

The goal: replace a 20-minute manual review process with a single dashboard that tells operations coordinators exactly what needs attention and why.

---

## Who It's For

**Primary user:** Freight operations coordinators and logistics analysts at small teams handling 50–200 shipments per week who:
- Have no data science department
- Have no enterprise TMS with AI built in
- Are currently making reactive decisions because they have no predictive visibility

---

## Core Value

Upload three raw documents → get a fully analyzed risk card without any human intervention.

---

## The AI Pipeline

Four parallel HuggingFace Inference API models, one per signal:

| Signal | Model | Input | Output |
|--------|-------|-------|--------|
| Invoice extraction | `microsoft/layoutlmv3-base` | PDF invoice | Structured fields + billing anomaly flag |
| Cargo damage | CLIP zero-shot (`openai/clip-vit-base-patch32`) | Damage photo | Severity score (none/minor/moderate/severe) |
| Entity recognition | `dslim/bert-base-NER` + `all-MiniLM-L6-v2` | Carrier note | Named entities (ORG, LOC, DATE) + carrier mismatch flag |
| Delay forecast | Regression on real public freight dataset | Route + carrier metadata | p50/p90 delay days + 7-day forecast |

Fused score = weighted combination of all four signals.

---

## Architecture (Existing)

- **Backend:** FastAPI + Celery (3 queues: doc, image, ner) + PostgreSQL + Redis
- **Frontend:** React 18 + Vite + TanStack Query + Recharts + Leaflet
- **Infra:** Docker Compose for Postgres/Redis/Flower; backend/frontend run on host
- **Deployment target:** Railway (or Render/Fly.io)

---

## Current State

The skeleton is largely in place but critical bugs prevent end-to-end operation:
- `send_task` name prefix mismatch — all uploads stuck in PENDING forever
- `fused_score` computation exists but is never called — always NULL
- Delay forecast columns exist in schema but no worker populates them
- ViT (ImageNet) used for damage detection — wrong model, no damage labels
- `asyncio.get_event_loop()` deprecated pattern throughout workers
- Alembic has no initial migration — tables may not exist

---

## Success Criteria

1. Upload 3 files → risk card populated in <40 seconds, no manual steps
2. All four AI signals contribute real values (not NULL, not placeholder)
3. Dashboard shows fused risk score, damage severity, billing flag, delay forecast, and incident feed
4. Deployable with a single `docker-compose up` (or equivalent)
5. Live URL shareable as portfolio piece

---

## Out of Scope (v1)

- User authentication / multi-tenant isolation
- Mobile app
- Webhook integrations with external TMS systems
- Real-time carrier tracking APIs

---

## Delay Forecast Dataset

Use a real public freight/shipping delay dataset (e.g. BTS T-100, Kaggle shipping datasets). Research and selection happens in Phase 3. Data is seeded into the DB or loaded at worker startup to keep the project self-contained.

---

*Project initialized: 2026-03-28*
