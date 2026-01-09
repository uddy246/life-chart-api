from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Any


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: dict[str, int] = defaultdict(int)
        self._errors: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)

    def record(self, endpoint: str, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self._requests[endpoint] += 1
            if status_code >= 400:
                self._errors[endpoint] += 1
            bucket = self._latencies[endpoint]
            bucket.append(latency_ms)
            if len(bucket) > 2000:
                del bucket[:1000]

    def _percentile(self, values: list[float], percentile: float) -> float:
        if not values:
            return 0.0
        values_sorted = sorted(values)
        index = int(round((len(values_sorted) - 1) * percentile))
        return values_sorted[index]

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            requests = dict(sorted(self._requests.items()))
            errors = dict(sorted(self._errors.items()))
            latency = {}
            for endpoint, values in sorted(self._latencies.items()):
                latency[endpoint] = {
                    "p50": round(self._percentile(values, 0.5), 2),
                    "p95": round(self._percentile(values, 0.95), 2),
                }
            return {
                "requests": requests,
                "errors": errors,
                "latency_ms": latency,
            }


METRICS = MetricsRegistry()
