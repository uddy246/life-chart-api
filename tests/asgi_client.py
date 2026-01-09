from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.parse import urlencode


async def _call_app(app, method: str, path: str, *, params: dict | None = None, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict[str, str], bytes]:
    query_string = urlencode(params or {}).encode()
    request_body = json.dumps(body).encode() if body is not None else b""
    raw_headers = [
        (b"host", b"testserver"),
    ]
    if body is not None:
        raw_headers.append((b"content-type", b"application/json"))
    if headers:
        for key, value in headers.items():
            raw_headers.append((key.lower().encode(), str(value).encode()))

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method.upper(),
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string,
        "headers": raw_headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
    }

    response_status = 500
    response_headers: list[tuple[bytes, bytes]] = []
    response_body = b""

    async def receive():
        return {"type": "http.request", "body": request_body, "more_body": False}

    async def send(message):
        nonlocal response_status, response_headers, response_body
        if message["type"] == "http.response.start":
            response_status = message["status"]
            response_headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            response_body += message.get("body", b"")

    await app(scope, receive, send)

    headers_dict = {key.decode().lower(): value.decode() for key, value in response_headers}
    return response_status, headers_dict, response_body


def call_app(app, method: str, path: str, *, params: dict | None = None, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict[str, str], Any]:
    status, resp_headers, resp_body = asyncio.run(
        _call_app(app, method, path, params=params, body=body, headers=headers)
    )
    if resp_body:
        try:
            payload = json.loads(resp_body.decode())
        except json.JSONDecodeError:
            payload = resp_body.decode()
    else:
        payload = None
    return status, resp_headers, payload
