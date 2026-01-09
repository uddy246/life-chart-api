from life_chart_api.main import app
from tests.asgi_client import call_app


def test_error_envelope_rate_limited():
    params = {
        "name": "Example Person",
        "date": "1999-02-26",
        "time": "14:00:00",
        "timezone": "UTC",
        "city": "Hyderabad",
        "region": "Telangana",
        "country": "India",
        "lat": 17.385,
        "lon": 78.4867,
        "from": "2026-01",
        "to": "2027-12",
        "include": "western,vedic,chinese",
        "granularity": "month",
    }
    headers = {"X-Forwarded-For": "9.9.9.9"}

    last_payload = None
    last_status = None
    for _ in range(61):
        last_status, _, last_payload = call_app(
            app, "GET", "/profile/forecast", params=params, headers=headers
        )

    assert last_status == 429
    assert last_payload["error"]["code"] == "RATE_LIMITED"
    assert last_payload["error"].get("requestId")
