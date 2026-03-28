from pydantic import BaseModel


class UploadResponse(BaseModel):
    shipment_id: int
    task_ids: dict[str, str]  # {"doc": task_id, "image": task_id, "ner": task_id}
    message: str
