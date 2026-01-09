from life_chart_api.main import app
from tests.asgi_client import call_app


def test_version_headers_narrative():
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
        "tone": "neutral",
    }
    status, headers, _ = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    assert headers.get("x-api-version")
    assert headers.get("x-schema-version")
