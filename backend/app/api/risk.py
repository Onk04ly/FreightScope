from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.risk_result import RiskResult
from app.schemas.risk import RiskCard

router = APIRouter(tags=["risk"])


@router.get("/risk/{shipment_id}", response_model=RiskCard)
async def get_risk_card(shipment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RiskResult).where(RiskResult.shipment_id == shipment_id)
    )
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk result not found")
    return risk
