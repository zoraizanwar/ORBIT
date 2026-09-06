from app.tasks.health import health_check_task


def test_celery_health_task_execution():
    """Verify that the trivial Celery health check task executes and returns expected status."""
    result = health_check_task()
    assert isinstance(result, dict)
    assert result["status"] == "healthy"
    assert result["task_name"] == "app.tasks.health.health_check_task"
    assert "timestamp_utc" in result
    assert "message" in result
