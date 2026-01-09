from life_chart_api.main import app
from tests.asgi_client import call_app


def test_request_id_propagated_to_error_envelope():
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
        "from": "2026-13",
        "to": "2027-12",
        "include": "western,vedic,chinese",
    }
    status, headers, payload = call_app(
        app, "GET", "/profile/forecast", params=params, headers={"X-Request-Id": "req-test"}
    )
    assert status == 400
    assert headers.get("x-request-id") == "req-test"
    assert payload["error"].get("requestId") == "req-test"
