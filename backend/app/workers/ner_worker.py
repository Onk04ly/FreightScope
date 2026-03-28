"""
NER worker — extracts entities from carrier notes via bert-base-NER,
then deduplicates via all-MiniLM-L6-v2 sentence embeddings.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.document import Document
from app.models.risk_result import RiskResult
from app.services.hf_client import infer
from app.workers.celery_app import celery_app

NER_MODEL = "dslim/bert-base-NER"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_COSINE_DEDUP_THRESHOLD = 0.92


def _cosine_sim(a: list[float], b: list[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b + 1e-9)


def _dedup_entities(entities: list[dict], embeddings: list[list[float]]) -> list[dict]:
    """Remove near-duplicate entity words using cosine similarity on embeddings."""
    kept: list[int] = []
    for i, emb in enumerate(embeddings):
        is_dup = False
        for j in kept:
            if _cosine_sim(emb, embeddings[j]) > _COSINE_DEDUP_THRESHOLD:
                is_dup = True
                break
        if not is_dup:
            kept.append(i)
    return [entities[i] for i in kept]


@celery_app.task(name="app.workers.ner_worker.extract_entities", bind=True, max_retries=3)
def extract_entities(self, document_id: int) -> dict:
    return asyncio.get_event_loop().run_until_complete(_extract_entities(document_id))


async def _extract_entities(document_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one()

        text = open(doc.file_path, encoding="utf-8", errors="ignore").read()[:2000]

        # Step 1: NER
        ner_response = await infer(NER_MODEL, {"inputs": text})
        # ner_response: list of {entity_group, score, word, start, end}
        entities: list[dict] = []
        for item in (ner_response or []):
            if item.get("score", 0) > 0.75:
                entities.append({
                    "type": item.get("entity_group", item.get("entity", "")),
                    "word": item.get("word", ""),
                })

        # Step 2: Deduplicate via sentence embeddings
        if len(entities) > 1:
            words = [e["word"] for e in entities]
            embed_response = await infer(EMBED_MODEL, {"inputs": words})
            # embed_response: list of embeddings (list of floats)
            if embed_response and len(embed_response) == len(entities):
                entities = _dedup_entities(entities, embed_response)

        # Group by entity type
        grouped: dict[str, list[str]] = {}
        for e in entities:
            grouped.setdefault(e["type"], []).append(e["word"])

        rr_result = await db.execute(
            select(RiskResult).where(RiskResult.shipment_id == doc.shipment_id)
        )
        risk = rr_result.scalar_one()
        risk.ner_entities = grouped

        doc.processed_at = datetime.now(timezone.utc)
        await db.commit()

        return {"document_id": document_id, "entities": grouped}
