try:
    from fastapi.testclient import TestClient
    _HAS_TESTCLIENT = True
except RuntimeError:
    TestClient = None
    _HAS_TESTCLIENT = False

from life_chart_api.main import app
from life_chart_api.routes.profile_forecast import ForecastRequest, get_forecast


def _get_forecast(params: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.get("/profile/forecast", params=params)
        assert response.status_code == 200
        return response.json()
    model = ForecastRequest.model_validate(params)
    return get_forecast(model)


def test_profile_forecast_ranking_ordering():
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

    response_json = _get_forecast(params)
    windows = response_json.get("topWindows", [])

    keys = [
        (
            -float(window.get("confidence", 0.0)),
            -float(window.get("intensity", 0.0)),
            str(window.get("start", "")),
            str(window.get("windowId", "")),
        )
        for window in windows
    ]
    assert keys == sorted(keys)

    for window in windows:
        evidence_ids = window.get("evidenceCycleIds", [])
        assert evidence_ids == sorted(evidence_ids)
