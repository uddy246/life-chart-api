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


def _intersection_signatures(response_json: dict) -> list[tuple[str, tuple[str, ...], tuple[str, ...]]]:
    signatures = []
    for cycle in response_json.get("cycles", []):
        if cycle.get("system") != "intersection":
            continue
        themes = tuple(cycle.get("themes", []))
        evidence_ids = tuple(
            entry.get("value", {}).get("cycleId", "")
            for entry in cycle.get("evidence", [])
            if isinstance(entry, dict)
        )
        signatures.append((cycle.get("cycleId", ""), themes, evidence_ids))
    return signatures


def test_profile_timeline_intersection_time_changes_with_input():
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
        "include": "vedic,chinese,western,intersection_time",
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
        "include": "vedic,chinese,western,intersection_time",
        "granularity": "month",
    }

    response_a = _get_timeline(params_a)
    response_b = _get_timeline(params_b)

    assert _intersection_signatures(response_a) != _intersection_signatures(response_b)
