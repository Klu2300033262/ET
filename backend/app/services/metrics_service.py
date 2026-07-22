import threading
from typing import Dict, Any

class MetricsService:
    """Lightweight thread-safe service to track and aggregate real-time system metrics."""
    def __init__(self):
        self._lock = threading.Lock()
        self.ai_requests = 0
        self.search_requests = 0
        self.total_confidence = 0.0
        self.confidence_count = 0
        self.total_processing_time_ms = 0.0
        self.processing_count = 0

    def record_chat(self, confidence: float):
        with self._lock:
            self.ai_requests += 1
            self.total_confidence += confidence
            self.confidence_count += 1

    def record_search(self):
        with self._lock:
            self.search_requests += 1

    def record_processing(self, time_ms: float):
        with self._lock:
            self.processing_count += 1
            self.total_processing_time_ms += time_ms

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            avg_conf = round(self.total_confidence / self.confidence_count, 3) if self.confidence_count > 0 else 0.0
            avg_proc = round(self.total_processing_time_ms / self.processing_count, 2) if self.processing_count > 0 else 0.0
            return {
                "ai_requests": self.ai_requests,
                "search_requests": self.search_requests,
                "avg_confidence": avg_conf,
                "avg_processing_time_ms": avg_proc
            }

metrics_service = MetricsService()
