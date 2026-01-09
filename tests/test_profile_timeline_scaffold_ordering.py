try:
    from fastapi.testclient import TestClient
    _HAS_TESTCLIENT = True
except RuntimeError:
    TestClient = None
    _HAS_TESTCLIENT = False

from life_chart_api.main import app
from life_chart_api.routes.profile_timeline import TimelineScaffoldRequest, get_timeline_scaffold


def _get_scaffold(params: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.get("/profile/timeline/scaffold", params=params)
        assert response.status_code == 200
        return response.json()
    model = TimelineScaffoldRequest.model_validate(params)
    return get_timeline_scaffold(model)


def test_profile_timeline_scaffold_ordering():
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
    }

    response_json = _get_scaffold(params)
    cycles = response_json.get("cycles", [])

    keys = [
        (cycle.get("start", ""), cycle.get("end", ""), cycle.get("system", ""), cycle.get("cycleId", ""))
        for cycle in cycles
    ]
    assert keys == sorted(keys)
