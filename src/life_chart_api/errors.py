from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class APIError(Exception):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None
    status_code: int = 400


def error_envelope(
    *,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details:
        payload["error"]["details"] = details
    if request_id:
        payload["error"]["requestId"] = request_id
    return payload
