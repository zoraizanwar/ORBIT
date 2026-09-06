import sys
from celery import Celery
from app.core.config import settings

# Initialize Celery application
celery_app = Celery(
    "orbit_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.health"],
)

# Windows-compatible pool configuration
# On Windows, Celery prefork can have issues; 'solo' or 'threads' is recommended for local development
worker_pool = "solo" if sys.platform.startswith("win") else "prefork"

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max for heavy tasks
    worker_prefetch_multiplier=1,
    worker_pool=worker_pool,
)
