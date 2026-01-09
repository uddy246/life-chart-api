try:
    from fastapi.testclient import TestClient
    _HAS_TESTCLIENT = True
except RuntimeError:
    TestClient = None
    _HAS_TESTCLIENT = False

from life_chart_api.main import app
from life_chart_api.routes.profile_timeline import TimelineRequest, get_timeline


def _get_timeline(params: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.get("/profile/timeline", params=params)
        assert response.status_code == 200
        return response.json()
    model = TimelineRequest.model_validate(params)
    return get_timeline(model)


def _first_cycle_id(response_json: dict) -> str | None:
    cycles = response_json.get("cycles", [])
    if cycles:
        return cycles[0].get("cycleId")
    return None


def test_profile_timeline_chinese_changes_with_input():
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
        "include": "chinese",
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
        "include": "chinese",
    }

    response_a = _get_timeline(params_a)
    response_b = _get_timeline(params_b)

    cycle_a = _first_cycle_id(response_a)
    cycle_b = _first_cycle_id(response_b)

    assert cycle_a is not None
    assert cycle_b is not None
    assert cycle_a != cycle_b
