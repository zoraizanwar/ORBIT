import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("orbit.observability")


class AnalysisLifecycleTracker:
    """
    Structured Local Observability & Audit Logger for ORBIT Analysis Runs.
    Tracks execution timing, algorithm versions, status transitions, and error sanitization.
    """

    SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "credentials", "authorization"}

    @classmethod
    def sanitize_payload(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively removes sensitive keys from logged payloads."""
        sanitized = {}
        for k, v in data.items():
            if k.lower() in cls.SENSITIVE_KEYS:
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = cls.sanitize_payload(v)
            elif isinstance(v, list):
                sanitized[k] = [
                    cls.sanitize_payload(item) if isinstance(item, dict) else item
                    for item in v
                ]
            else:
                sanitized[k] = v
        return sanitized

    def __init__(
        self,
        analysis_type: str,
        aoi_id: str,
        algorithm_version: str = "ORBIT-v1.0.0",
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.analysis_id = str(uuid.uuid4())
        self.analysis_type = analysis_type
        self.aoi_id = aoi_id
        self.algorithm_version = algorithm_version
        self.parameters = self.sanitize_payload(parameters or {})
        self.status = "INITIALIZED"
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: Optional[float] = None
        self.error_message: Optional[str] = None

    def start(self) -> None:
        self.status = "RUNNING"
        self.start_time = time.time()
        self._log_event("ANALYSIS_STARTED")

    def complete(self, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = "COMPLETED"
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - (self.start_time or self.end_time)) * 1000, 2)
        summary = self.to_dict()
        if metrics:
            summary["metrics"] = metrics
        self._log_event("ANALYSIS_COMPLETED", extra=summary)
        return summary

    def fail(self, error: Exception) -> Dict[str, Any]:
        self.status = "FAILED"
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - (self.start_time or self.end_time)) * 1000, 2)
        self.error_message = str(error)[:300]
        summary = self.to_dict()
        self._log_event("ANALYSIS_FAILED", level=logging.ERROR, extra=summary)
        return summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "analysis_type": self.analysis_type,
            "aoi_id": self.aoi_id,
            "status": self.status,
            "algorithm_version": self.algorithm_version,
            "duration_ms": self.duration_ms,
            "parameters": self.parameters,
            "error_message": self.error_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _log_event(self, event_name: str, level: int = logging.INFO, extra: Optional[Dict[str, Any]] = None) -> None:
        log_entry = {
            "event": event_name,
            "data": extra or self.to_dict(),
        }
        logger.log(level, json.dumps(log_entry))
