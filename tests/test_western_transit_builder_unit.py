from life_chart_api.temporal.western_transits import build_western_transit_cycles


def test_western_transit_builder_unit():
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

    cycles = build_western_transit_cycles(
        birth=birth,
        range_from="2026-01",
        range_to="2027-12",
        as_of=None,
    )

    kinds = {cycle.get("kind") for cycle in cycles}
    assert "return_saturn" in kinds or "return_jupiter" in kinds or "transit_saturn_aspect" in kinds

    for cycle in cycles[:3]:
        assert cycle.get("cycleId")
