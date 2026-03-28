import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ShipmentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    origin_port: Mapped[str] = mapped_column(String(100))
    dest_port: Mapped[str] = mapped_column(String(100))
    carrier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus), default=ShipmentStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    documents: Mapped[list["Document"]] = relationship(back_populates="shipment")
    risk_result: Mapped["RiskResult | None"] = relationship(
        back_populates="shipment", uselist=False
    )
