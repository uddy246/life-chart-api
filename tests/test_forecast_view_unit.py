from life_chart_api.temporal.forecast_view import build_forecast_response


def test_forecast_view_domain_mapping():
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
    cycles = [
        {
            "cycleId": "cycle-1",
            "system": "intersection",
            "kind": "window",
            "domain": "growth",
            "themes": ["window:2026-01", "structure_discipline"],
            "start": "2026-01-01",
            "end": "2026-01-31",
            "intensity": 0.6,
            "polarity": "supporting",
            "evidence": [
                {
                    "source": "timeline.cycle",
                    "value": {"system": "western", "cycleId": "w1"},
                    "weight": 0.4,
                    "note": "test",
                }
            ],
            "notes": [],
        },
        {
            "cycleId": "cycle-2",
            "system": "intersection",
            "kind": "window",
            "domain": "growth",
            "themes": ["window:2026-02", "love_harmony"],
            "start": "2026-02-01",
            "end": "2026-02-28",
            "intensity": 0.5,
            "polarity": "neutral",
            "evidence": [
                {
                    "source": "timeline.cycle",
                    "value": {"system": "vedic", "cycleId": "v1"},
                    "weight": 0.4,
                    "note": "test",
                }
            ],
            "notes": [],
        },
    ]

    response = build_forecast_response(
        name=None,
        birth=birth,
        range_from="2026-01",
        range_to="2026-03",
        granularity="month",
        as_of=None,
        intersection_cycles=cycles,
    )

    assert response["byDomain"]["career"]
    assert response["byDomain"]["relationships"]
