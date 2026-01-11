from life_chart_api.main import app
from life_chart_api.routes.profile_forecast import ForecastRequest, get_forecast
from tests.asgi_client import call_app


def _get_forecast(params: dict) -> dict:
    model = ForecastRequest.model_validate(params)
    return get_forecast(model)


def _get_narrative(params: dict) -> dict:
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    return payload


def test_profile_narrative_ordering():
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

    forecast = _get_forecast(params)
    narrative = _get_narrative(params)

    forecast_ids = [window.get("windowId") for window in forecast.get("topWindows", [])]
    narrative_ids = [
        window.get("windowId")
        for window in narrative.get("narrative", {}).get("windows", [])
    ]
    assert narrative_ids == forecast_ids

    for window in narrative.get("narrative", {}).get("windows", []):
        for citation in window.get("citations", []):
            evidence_ids = citation.get("evidenceCycleIds", [])
            assert evidence_ids == sorted(evidence_ids)
