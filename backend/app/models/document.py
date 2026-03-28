import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocType(str, enum.Enum):
    invoice = "invoice"
    image = "image"
    note = "note"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.id", ondelete="CASCADE"))
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType))
    file_path: Mapped[str] = mapped_column(String(500))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    shipment: Mapped["Shipment"] = relationship(back_populates="documents")
