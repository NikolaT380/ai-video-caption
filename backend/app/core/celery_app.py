import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "video_tasks",
    broker=broker_url,
    backend=result_backend,
    include=["app.workers.tasks.process_video"],
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
)