import os
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.document import DocType, Document
from app.models.risk_result import RiskResult
from app.models.shipment import Shipment
from app.schemas.upload import UploadResponse
from app.workers.celery_app import celery_app

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_shipment(
    origin_port: str = Form(...),
    dest_port: str = Form(...),
    carrier: str = Form(""),
    invoice: UploadFile | None = File(None),
    cargo_image: UploadFile | None = File(None),
    carrier_note: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    shipment = Shipment(
        origin_port=origin_port,
        dest_port=dest_port,
        carrier=carrier or None,
    )
    db.add(shipment)
    await db.flush()

    risk = RiskResult(shipment_id=shipment.id)
    db.add(risk)
    await db.flush()

    task_ids: dict[str, str] = {}
    upload_path = settings.upload_dir
    os.makedirs(upload_path, exist_ok=True)

    async def _save(file: UploadFile, doc_type: DocType) -> Document:
        ext = os.path.splitext(file.filename or "")[1] or ""
        fname = f"{uuid.uuid4()}{ext}"
        fpath = os.path.join(upload_path, fname)
        content = await file.read()
        with open(fpath, "wb") as f:
            f.write(content)
        doc = Document(shipment_id=shipment.id, doc_type=doc_type, file_path=fpath)
        db.add(doc)
        await db.flush()
        return doc

    if invoice:
        doc = await _save(invoice, DocType.invoice)
        task = celery_app.send_task(
            "workers.doc_worker.process_invoice",
            args=[doc.id],
            queue="doc",
        )
        task_ids["doc"] = task.id

    if cargo_image:
        doc = await _save(cargo_image, DocType.image)
        task = celery_app.send_task(
            "workers.image_worker.classify_cargo",
            args=[doc.id],
            queue="image",
        )
        task_ids["image"] = task.id

    if carrier_note:
        doc = await _save(carrier_note, DocType.note)
        task = celery_app.send_task(
            "workers.ner_worker.extract_entities",
            args=[doc.id],
            queue="ner",
        )
        task_ids["ner"] = task.id

    await db.commit()

    return UploadResponse(
        shipment_id=shipment.id,
        task_ids=task_ids,
        message="Upload accepted. Processing started.",
    )
