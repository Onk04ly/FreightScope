"""
Integration tests for FastAPI endpoints using httpx AsyncClient.
Requires a running PostgreSQL database (set DB_URL in environment).
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_list_shipments_empty(client: AsyncClient):
    response = await client.get("/api/shipments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_risk_card_not_found(client: AsyncClient):
    response = await client.get("/api/risk/99999")
    assert response.status_code == 404
