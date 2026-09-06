import time
from app.services.observability import AnalysisLifecycleTracker


def test_analysis_lifecycle_tracking():
    tracker = AnalysisLifecycleTracker(
        analysis_type="SPECTRAL_INDEX_EXTRACTION",
        aoi_id="aoi-test-001",
        algorithm_version="ORBIT-NDVI-v1",
        parameters={"metric": "NDVI", "token": "secret-12345", "password": "mypassword"},
    )

    assert tracker.parameters["token"] == "[REDACTED]"
    assert tracker.parameters["password"] == "[REDACTED]"
    assert tracker.parameters["metric"] == "NDVI"
    assert tracker.status == "INITIALIZED"

    tracker.start()
    assert tracker.status == "RUNNING"
    time.sleep(0.01)

    summary = tracker.complete(metrics={"mean_ndvi": 0.45})
    assert summary["status"] == "COMPLETED"
    assert summary["duration_ms"] > 0
    assert summary["metrics"]["mean_ndvi"] == 0.45


def test_analysis_lifecycle_failure_tracking():
    tracker = AnalysisLifecycleTracker(
        analysis_type="CHANGE_DETECTION",
        aoi_id="aoi-test-002",
    )
    tracker.start()
    summary = tracker.fail(ValueError("Invalid window boundaries"))

    assert summary["status"] == "FAILED"
    assert "Invalid window boundaries" in summary["error_message"]
    assert summary["duration_ms"] is not None
