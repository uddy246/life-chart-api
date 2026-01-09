from life_chart_api.schemas.profile_response_builder import build_profile_response
from life_chart_api.synthesis.intersection_engine_v2 import build_intersection_v2


def test_intersection_v2_deterministic():
    birth = {
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
    }
    response = build_profile_response(name="Example Person", birth=birth, numerology=None)
    v2_a = build_intersection_v2(response)
    v2_b = build_intersection_v2(response)
    assert v2_a == v2_b
