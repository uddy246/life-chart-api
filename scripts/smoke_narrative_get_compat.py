import sys
import requests

API = "http://127.0.0.1:8000"


def _assert(status: bool, message: str) -> None:
    if not status:
        print(message)
        raise AssertionError(message)


def main() -> int:
    ok_query = f"{API}/profile/narrative?query.name=Ada%20Lovelace&query.dob=1990-01-01"
    ok_flat = f"{API}/profile/narrative?name=Ada%20Lovelace&dob=1990-01-01"
    bad_flat = f"{API}/profile/narrative?name=Ada%20Lovelace"

    r1 = requests.get(ok_query, timeout=30)
    _assert(r1.status_code == 200, f"query.* request failed: {r1.status_code} {r1.text}")
    _assert("profile" in r1.json(), "query.* response missing profile")

    r2 = requests.get(ok_flat, timeout=30)
    _assert(r2.status_code == 200, f"flat request failed: {r2.status_code} {r2.text}")
    _assert("profile" in r2.json(), "flat response missing profile")

    r3 = requests.get(bad_flat, timeout=30)
    _assert(r3.status_code == 422, f"missing dob should be 422: {r3.status_code} {r3.text}")
    body = r3.json()
    _assert(
        any(item.get("loc") == ["query", "dob"] for item in body.get("detail", [])),
        "missing dob not reported in detail",
    )

    print("smoke_narrative_get_compat: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
