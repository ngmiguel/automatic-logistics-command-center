from celery import Celery

from alcc.config import get_settings

settings = get_settings()

celery_app = Celery(
    "alcc",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "alcc.worker.tasks.optimize_routes": {"queue": "routing"},
        "alcc.worker.tasks.schedule_maintenance": {"queue": "maintenance"},
        "alcc.worker.tasks.compute_analytics": {"queue": "analytics"},
        "alcc.worker.tasks.send_notification_batch": {"queue": "notifications"},
    },
)

celery_app.autodiscover_tasks(["alcc.worker"])
