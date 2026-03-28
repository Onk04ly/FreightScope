"""
Document worker — processes invoice PDFs via LayoutLMv3-base on HF Inference API.
Pipeline: pdf2image → base64 encode pages → LayoutLMv3 Document QA → extract fields.
"""
import asyncio
import base64
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.document import Document
from app.models.risk_result import RiskResult
from app.services.hf_client import infer
from app.workers.celery_app import celery_app

MODEL_ID = "microsoft/layoutlmv3-base"

# Questions to extract from invoice
_QUESTIONS = [
    "What is the origin?",
    "What is the destination?",
    "What is the billed amount?",
    "What are the HS codes?",
    "What is the weight?",
]


def _pdf_to_base64_pages(file_path: str) -> list[str]:
    from pdf2image import convert_from_path

    images = convert_from_path(file_path, dpi=150)
    encoded = []
    for img in images[:3]:  # process first 3 pages max
        import io

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        encoded.append(base64.b64encode(buf.getvalue()).decode())
    return encoded


@celery_app.task(name="app.workers.doc_worker.process_invoice", bind=True, max_retries=3)
def process_invoice(self, document_id: int) -> dict:
    return asyncio.get_event_loop().run_until_complete(_process_invoice(document_id))


async def _process_invoice(document_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one()

        pages_b64 = _pdf_to_base64_pages(doc.file_path)
        extracted: dict = {}

        for question in _QUESTIONS:
            for page_b64 in pages_b64:
                try:
                    payload = {
                        "inputs": {
                            "question": question,
                            "image": page_b64,
                        }
                    }
                    answer = await infer(MODEL_ID, payload)
                    if answer and answer.get("score", 0) > 0.5:
                        extracted[question] = answer.get("answer", "")
                        break
                except Exception:
                    continue

        # Detect billing anomaly: billed amount present but unusually high (placeholder logic)
        billing_anomaly = False
        billed_str = extracted.get("What is the billed amount?", "")
        if billed_str:
            try:
                amount = float("".join(c for c in billed_str if c.isdigit() or c == "."))
                billing_anomaly = amount > 100_000
            except ValueError:
                pass

        # Update risk result
        rr_result = await db.execute(
            select(RiskResult).where(RiskResult.shipment_id == doc.shipment_id)
        )
        risk = rr_result.scalar_one()
        risk.billing_anomaly_flag = billing_anomaly

        doc.processed_at = datetime.now(timezone.utc)
        await db.commit()

        return {"document_id": document_id, "extracted": extracted, "billing_anomaly": billing_anomaly}
