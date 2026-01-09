try:
    from fastapi.testclient import TestClient
    _HAS_TESTCLIENT = True
except RuntimeError:
    TestClient = None
    _HAS_TESTCLIENT = False

from life_chart_api.main import app
from life_chart_api.routes.profile_compute import ProfileComputeRequest, compute_profile


def _post_profile(payload: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.post("/profile/compute", json=payload)
        assert response.status_code == 200
        return response.json()
    model = ProfileComputeRequest.model_validate(payload)
    return compute_profile(model)


def test_numerology_deterministic():
    payload = {
        "name": "Example Person",
        "birth": {
            "date": "1999-02-26",
            "time": "14:00:00",
            "timezone": "UTC",
            "location": {
                "city": "Hyderabad",
                "region": "Telangana",
                "country": "India",
                "lat": 17.385,
                "lon": 78.4867,
            },
        },
    }

    response_a = _post_profile(payload)
    response_b = _post_profile(payload)
    numerology_a = response_a.get("systems", {}).get("numerology", {})
    numerology_b = response_b.get("systems", {}).get("numerology", {})
    assert numerology_a == numerology_b
