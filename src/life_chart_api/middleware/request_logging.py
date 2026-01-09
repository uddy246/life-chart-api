from __future__ import annotations

import logging
import time

from starlette.requests import Request


async def request_logging_middleware(request: Request, call_next):
    logger = logging.getLogger("life_chart_api")
    start = time.monotonic()
    status_code = 500
    error = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as exc:  # pragma: no cover - logging side-effect
        error = exc
        raise
    finally:
        latency_ms = (time.monotonic() - start) * 1000.0
        extra = {
            "requestId": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "latency_ms": round(latency_ms, 2),
        }
        level = logging.ERROR if error else logging.INFO
        logger.log(level, "request_completed", extra={"extra": extra})
