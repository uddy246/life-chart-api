import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from life_chart_api.main import app
from tests.asgi_client import call_app


def _assert(status: bool, message: str) -> None:
    if not status:
        print(message)
        raise AssertionError(message)


def _has_legacy_fields(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False
    if "overview" not in payload or "headline" not in payload or "windows" not in payload:
        return False
    return True


def main() -> int:
    ok_query = {"query.name": "Ada Lovelace", "query.dob": "1990-01-01"}
    ok_flat = {"name": "Ada Lovelace", "dob": "1990-01-01"}
    bad_flat = {"name": "Ada Lovelace"}

    status, _, payload = call_app(app, "GET", "/profile/narrative", params=ok_query)
    _assert(status == 200, f"query.* request failed: {status} {payload}")
    _assert("profile" in payload, "query.* response missing profile")
    _assert("intersection" in payload, "query.* response missing intersection")
    _assert("narrative" in payload, "query.* response missing narrative")
    _assert(
        _has_legacy_fields(payload.get("intersection", {})),
        "query.* response missing intersection legacy overview/headline/windows fields",
    )
    _assert(
        _has_legacy_fields(payload),
        "query.* response missing top-level legacy overview/headline/windows fields",
    )

    status, _, payload = call_app(app, "GET", "/profile/narrative", params=ok_flat)
    _assert(status == 200, f"flat request failed: {status} {payload}")
    _assert("profile" in payload, "flat response missing profile")
    _assert("intersection" in payload, "flat response missing intersection")
    _assert("narrative" in payload, "flat response missing narrative")
    _assert(
        _has_legacy_fields(payload.get("intersection", {})),
        "flat response missing intersection legacy overview/headline/windows fields",
    )
    _assert(
        _has_legacy_fields(payload),
        "flat response missing top-level legacy overview/headline/windows fields",
    )

    status, _, body = call_app(app, "GET", "/profile/narrative", params=bad_flat)
    _assert(status == 422, f"missing dob should be 422: {status} {body}")
    _assert(
        any(item.get("loc") == ["query", "dob"] for item in body.get("detail", [])),
        "missing dob not reported in detail",
    )

    print("smoke_narrative_get_compat: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
