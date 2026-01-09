from life_chart_api.schemas.profile_response_builder import build_profile_response
from life_chart_api.synthesis.intersection_engine import build_intersection


def test_intersection_engine_deterministic():
    birth = {
        "date": "1999-02-26",
        "time": "14:00:00",
        "timezone": "UTC",
        "location": {
            "city": "Hyderabad",
            "region": "Telangana",
            "country": "India",
            "lat": 0,
            "lon": 0,
        },
    }
    response = build_profile_response(name="Example Person", birth=birth, numerology=None)
    intersection_a = build_intersection(response)
    intersection_b = build_intersection(response)
    assert intersection_a == intersection_b
