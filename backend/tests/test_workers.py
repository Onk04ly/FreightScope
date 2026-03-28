"""
Unit tests for worker service logic (no real HF API calls).
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.services.risk_scorer import RiskSignals, compute_fused_score, zscore_anomaly


def test_fused_score_all_clear():
    signals = RiskSignals(billing_anomaly=False, damage_severity="none", delay_days_p50=0.0)
    score = compute_fused_score(signals)
    assert score == 0.0


def test_fused_score_all_risk():
    signals = RiskSignals(
        billing_anomaly=True, damage_severity="severe", delay_days_p50=14.0, ner_mismatch=True
    )
    score = compute_fused_score(signals)
    assert score == 1.0


def test_fused_score_partial():
    signals = RiskSignals(billing_anomaly=True, damage_severity="moderate")
    score = compute_fused_score(signals)
    assert 0.0 < score < 1.0


def test_zscore_anomaly_detects_outlier():
    values = [1.0, 1.1, 0.9, 1.0, 100.0]
    flags = zscore_anomaly(values)
    assert flags[-1] is True
    assert all(not f for f in flags[:-1])


def test_zscore_anomaly_uniform():
    values = [5.0, 5.0, 5.0]
    flags = zscore_anomaly(values)
    assert all(not f for f in flags)


@pytest.mark.asyncio
async def test_hf_client_retries_on_503():
    """HF client should retry on 503 and eventually raise RuntimeError."""
    import httpx

    with patch("app.services.hf_client.asyncio.sleep", new_callable=AsyncMock):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 503
            mock_post.return_value = mock_response

            from app.services.hf_client import infer

            with pytest.raises(RuntimeError, match="unavailable"):
                await infer("test/model", {"inputs": "hello"})
