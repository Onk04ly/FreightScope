from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RiskResult(Base):
    __tablename__ = "risk_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"), unique=True
    )
    fused_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    delay_days_p50: Mapped[float | None] = mapped_column(Float, nullable=True)
    delay_days_p90: Mapped[float | None] = mapped_column(Float, nullable=True)
    billing_anomaly_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    damage_severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ner_entities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    incident_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    delay_forecast: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    shipment: Mapped["Shipment"] = relationship(back_populates="risk_result")
