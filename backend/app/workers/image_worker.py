"""
Image worker — classifies cargo damage severity via ViT-base-patch16-224.
Labels mapped to FreightScope severity scale: none / minor / moderate / severe.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.document import Document
from app.models.risk_result import RiskResult
from app.services.hf_client import infer_image
from app.workers.celery_app import celery_app

MODEL_ID = "google/vit-base-patch16-224"

# Map ViT ImageNet labels to damage severity buckets
_SEVERITY_KEYWORDS = {
    "severe": ["wreck", "damage", "broken", "crushed", "destroyed", "debris"],
    "moderate": ["dent", "scratch", "crack", "bent", "torn", "stained"],
    "minor": ["dirty", "wet", "worn", "faded", "smudge"],
}


def _map_label_to_severity(label: str) -> str:
    label_lower = label.lower()
    for severity, keywords in _SEVERITY_KEYWORDS.items():
        if any(kw in label_lower for kw in keywords):
            return severity
    return "none"


@celery_app.task(name="app.workers.image_worker.classify_cargo", bind=True, max_retries=3)
def classify_cargo(self, document_id: int) -> dict:
    return asyncio.get_event_loop().run_until_complete(_classify_cargo(document_id))


async def _classify_cargo(document_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one()

        predictions = await infer_image(MODEL_ID, doc.file_path)

        # predictions is a list of {label, score} dicts
        top_label = predictions[0]["label"] if predictions else "unknown"
        severity = _map_label_to_severity(top_label)

        rr_result = await db.execute(
            select(RiskResult).where(RiskResult.shipment_id == doc.shipment_id)
        )
        risk = rr_result.scalar_one()
        risk.damage_severity = severity

        doc.processed_at = datetime.now(timezone.utc)
        await db.commit()

        return {"document_id": document_id, "top_label": top_label, "severity": severity}
