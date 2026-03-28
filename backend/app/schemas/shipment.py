from datetime import datetime

from pydantic import BaseModel

from app.models.shipment import ShipmentStatus


class ShipmentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    origin_port: str
    dest_port: str
    carrier: str | None
    status: ShipmentStatus
    created_at: datetime
