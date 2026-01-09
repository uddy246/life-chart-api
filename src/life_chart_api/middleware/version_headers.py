from __future__ import annotations

from starlette.requests import Request

from life_chart_api.versioning import API_VERSION, schema_version_for_path


async def version_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = API_VERSION
    response.headers["X-Schema-Version"] = schema_version_for_path(request.url.path)
    return response
