from __future__ import annotations

import time

from starlette.requests import Request

from life_chart_api.metrics import METRICS


async def metrics_middleware(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    latency_ms = (time.monotonic() - start) * 1000.0
    route = request.scope.get("route")
    endpoint = route.path if route else request.url.path
    METRICS.record(endpoint, response.status_code, latency_ms)
    return response
