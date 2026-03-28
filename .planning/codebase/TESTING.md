# Testing Patterns

**Analysis Date:** 2026-03-28

## Test Framework

**Runner:**
- pytest 8.1.0+
- Config: no dedicated `pytest.ini` or `pyproject.toml` — pytest is invoked with defaults from the project root or `backend/` directory
- Async support: `pytest-asyncio` 0.23.0+ and `anyio` 4.3.0+ (both installed via `backend/requirements.txt`)

**Run Commands:**
```bash
cd backend
pytest tests/
pytest tests/test_workers.py         # Unit tests only (no DB required)
pytest tests/test_api.py             # Integration tests (requires PostgreSQL + env vars)
pytest tests/ -v --tb=short
```

## Test File Organization

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_api.py       # Integration tests — FastAPI endpoints via httpx AsyncClient
│   └── test_workers.py   # Unit tests — pure logic in services/, plus hf_client retry
└── app/
    └── ...               # No tests co-located with source
```

## Mocking

**Framework:** `unittest.mock` (stdlib) — `patch`, `AsyncMock`

- Mock `httpx.AsyncClient.post` for hf_client tests
- Mock `asyncio.sleep` alongside network calls
- Do NOT mock pure service functions (risk_scorer) — test them directly

## Test Types

**Unit Tests (`tests/test_workers.py`):** pure service logic, no DB/network

**Integration Tests (`tests/test_api.py`):** HTTP layer via httpx ASGITransport; requires live PostgreSQL

**E2E Tests:** Not present.

**Frontend Tests:** Not present — no Vitest/Jest/Testing Library configured.

## Coverage Gaps

| Area | Gap | Priority |
|------|-----|----------|
| `app/workers/` (doc/image/ner) | Completely untested | HIGH |
| `POST /api/upload` | File upload + task dispatch untested | HIGH |
| `app/api/ws.py` | WebSocket endpoint untested | MEDIUM |
| `infer_image` in hf_client | No test (only `infer` tested) | MEDIUM |
| Frontend `src/` | Zero tests, no runner configured | MEDIUM |
| DB session override | No conftest.py, no in-memory fixture | MEDIUM |
| `app/api/risk.py` success path | Only 404 path tested | LOW |

**No `conftest.py` exists** — add `backend/tests/conftest.py` for shared fixtures.

**`pytest-cov` not in requirements.txt** — coverage not enforced.

---

*Testing analysis: 2026-03-28*
