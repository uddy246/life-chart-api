from life_chart_api.main import app
from tests.asgi_client import call_app


def _get_narrative(params: dict) -> dict:
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    return payload


def _headline(response_json: dict) -> str:
    return response_json.get("narrative", {}).get("overview", {}).get("headline", "")


def test_profile_narrative_changes_with_input():
    params_a = {
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
    params_b = {
        "name": "Example Person",
        "date": "1999-07-26",
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

    response_a = _get_narrative(params_a)
    response_b = _get_narrative(params_b)

    assert _headline(response_a) != _headline(response_b)
