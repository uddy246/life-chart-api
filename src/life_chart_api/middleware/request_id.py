from __future__ import annotations

import uuid

from starlette.requests import Request


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id")
    if not request_id:
        request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response
