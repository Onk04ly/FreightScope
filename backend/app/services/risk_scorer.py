"""
Anomaly scoring logic using Pandas + NumPy.
Computes a fused risk score (0-1) from individual signals.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class RiskSignals:
    billing_anomaly: bool = False
    damage_severity: str | None = None  # none, minor, moderate, severe
    delay_days_p50: float | None = None
    ner_mismatch: bool = False  # carrier in note != carrier in shipment record


_DAMAGE_WEIGHTS = {"none": 0.0, "minor": 0.25, "moderate": 0.6, "severe": 1.0}
_DELAY_CAP_DAYS = 14.0  # delays beyond this cap at score=1.0


def compute_fused_score(signals: RiskSignals) -> float:
    """Z-score-style fusion of risk signals into a 0-1 score."""
    components: list[float] = []

    # Billing anomaly (binary)
    components.append(1.0 if signals.billing_anomaly else 0.0)

    # Damage severity
    damage_score = _DAMAGE_WEIGHTS.get(signals.damage_severity or "none", 0.0)
    components.append(damage_score)

    # Delay normalised to [0, 1]
    if signals.delay_days_p50 is not None:
        delay_score = min(signals.delay_days_p50 / _DELAY_CAP_DAYS, 1.0)
        components.append(delay_score)

    # NER carrier mismatch
    components.append(0.5 if signals.ner_mismatch else 0.0)

    return float(np.clip(np.mean(components), 0.0, 1.0))


def zscore_anomaly(values: list[float], threshold: float = 2.0) -> list[bool]:
    """Return a boolean mask for values that are outliers (|z| > threshold)."""
    arr = np.array(values, dtype=float)
    if arr.std() == 0:
        return [False] * len(values)
    z = (arr - arr.mean()) / arr.std()
    return (np.abs(z) > threshold).tolist()
