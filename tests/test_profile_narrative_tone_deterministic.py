from life_chart_api.main import app
from tests.asgi_client import call_app


def _get_narrative(params: dict) -> dict:
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    return payload.get("narrative", {})


def test_profile_narrative_tone_deterministic():
    base = {
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

    for tone in ("neutral", "direct", "reflective"):
        params = dict(base)
        params["tone"] = tone
        response_a = _get_narrative(params)
        response_b = _get_narrative(params)
        assert response_a == response_b
