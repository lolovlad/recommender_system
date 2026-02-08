import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://broker:6379/0")

celery_app = Celery(
    "recommender_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL[:-1] + "1",
    include=["src.recommender_system.presentation.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
)