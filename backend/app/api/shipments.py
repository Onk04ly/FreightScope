from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentRead

router = APIRouter(tags=["shipments"])


@router.get("/shipments", response_model=list[ShipmentRead])
async def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Shipment).order_by(Shipment.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()
