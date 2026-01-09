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


def _life_path_value(numerology: dict) -> int | None:
    primitives = numerology.get("primitives", {})
    life_path = primitives.get("life_path") if isinstance(primitives, dict) else None
    if not isinstance(life_path, dict):
        return None
    reduction = life_path.get("reduction")
    if isinstance(reduction, dict) and isinstance(reduction.get("final_value"), int):
        return reduction["final_value"]
    return None


def test_numerology_changes_with_input():
    payload_a = {
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
    payload_b = {
        "name": "Different Name",
        "birth": {
            "date": "1999-07-26",
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

    response_a = _post_profile(payload_a)
    response_b = _post_profile(payload_b)
    numerology_a = response_a.get("systems", {}).get("numerology", {})
    numerology_b = response_b.get("systems", {}).get("numerology", {})

    value_a = _life_path_value(numerology_a)
    value_b = _life_path_value(numerology_b)
    assert value_a is not None
    assert value_b is not None
    assert value_a != value_b
