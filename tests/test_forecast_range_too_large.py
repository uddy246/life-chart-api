from life_chart_api.main import app
from tests.asgi_client import call_app


def test_forecast_range_too_large():
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
        "from": "2020-01",
        "to": "2030-12",
        "include": "western,vedic,chinese",
        "granularity": "month",
    }
    status, _, payload = call_app(app, "GET", "/profile/forecast", params=params)
    assert status == 400
    assert payload["error"]["code"] == "INVALID_INPUT"
