from celery import Celery

from app.config import settings

celery_app = Celery(
    "freightscope",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.doc_worker",
        "app.workers.image_worker",
        "app.workers.ner_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.workers.doc_worker.*": {"queue": "doc"},
        "app.workers.image_worker.*": {"queue": "image"},
        "app.workers.ner_worker.*": {"queue": "ner"},
    },
    task_queues={
        "doc": {"exchange": "doc", "routing_key": "doc"},
        "image": {"exchange": "image", "routing_key": "image"},
        "ner": {"exchange": "ner", "routing_key": "ner"},
    },
)
