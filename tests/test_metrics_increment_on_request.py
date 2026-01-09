from life_chart_api.main import app
from life_chart_api.metrics import METRICS
from tests.asgi_client import call_app


def test_metrics_increment_on_request():
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
    call_app(app, "GET", "/profile/forecast", params=params)
    snapshot = METRICS.snapshot()
    assert snapshot["requests"].get("/profile/forecast", 0) >= 1
