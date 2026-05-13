import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "blog_api",
    broker=REDIS_URL,
    backend=REDIS_URL.replace("/0", "/1"),
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=["app.tasks.celery_tasks"],  # ← добавили автоимпорт задач
)