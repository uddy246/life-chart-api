from life_chart_api.main import app
from life_chart_api.routes import profile_compute
from tests.asgi_client import call_app


def test_profile_narrative_geocode_failure_returns_200(monkeypatch):
    def _raise_geocode(*_args, **_kwargs):
        raise RuntimeError("geocode blocked")

    monkeypatch.setattr(profile_compute, "geocode_location", _raise_geocode)

    params = {
        "name": "Example Person",
        "dob": "1999-02-26",
        "time": "14:00",
        "timezone": "UTC",
        "city": "Hyderabad",
        "region": "Telangana",
        "country": "India",
        "include": "western,vedic,chinese",
        "granularity": "month",
    }
    status, _, data = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    assert "profile" in data
    assert "intersection" in data
    assert "narrative" in data
    assert "geocoding_unavailable" in data.get("profile", {}).get("warnings", [])
