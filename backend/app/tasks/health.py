from datetime import datetime, timezone
from typing import Any, Dict
from app.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(name="app.tasks.health.health_check_task")
def health_check_task() -> Dict[str, Any]:
    """Trivial health check background task to verify Celery broker and worker connectivity."""
    logger.info("Executing Celery background health check task...")
    return {
        "status": "healthy",
        "task_name": "app.tasks.health.health_check_task",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "message": "Celery worker is operating nominally.",
    }
