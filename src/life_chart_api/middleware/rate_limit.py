from __future__ import annotations

import time
import uuid
from typing import Any, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse

from life_chart_api.errors import error_envelope


def create_rate_limit_middleware(*, max_requests: int = 60, window_seconds: int = 60) -> Callable:
    buckets: dict[str, dict[str, Any]] = {}

    def _client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def rate_limit_middleware(request: Request, call_next):
        key = _client_key(request)
        now = int(time.time())
        window_start = now - (now % window_seconds)
        bucket = buckets.get(key)
        if bucket is None or bucket["window_start"] != window_start:
            bucket = {"window_start": window_start, "count": 0}
            buckets[key] = bucket
        bucket["count"] += 1
        if bucket["count"] > max_requests:
            if not getattr(request.state, "request_id", None):
                request.state.request_id = str(uuid.uuid4())
            payload = error_envelope(
                code="RATE_LIMITED",
                message="Too many requests.",
                details=[{"path": "rate_limit", "issue": "request limit exceeded"}],
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(status_code=429, content=payload)
        return await call_next(request)

    return rate_limit_middleware
