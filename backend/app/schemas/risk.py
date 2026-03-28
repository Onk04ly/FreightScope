from datetime import datetime

from pydantic import BaseModel


class DelayForecastDay(BaseModel):
    date: str
    p50: float
    p90: float


class RiskCard(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    shipment_id: int
    fused_score: float | None
    delay_days_p50: float | None
    delay_days_p90: float | None
    billing_anomaly_flag: bool
    damage_severity: str | None
    ner_entities: dict | None
    incident_summary: str | None
    delay_forecast: list[DelayForecastDay] | None
    created_at: datetime
