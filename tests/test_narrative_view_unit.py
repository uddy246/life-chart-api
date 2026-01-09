from life_chart_api.narrative.narrative_view import build_narrative_response


def test_narrative_view_unit():
    forecast = {
        "meta": {"version": "phase2.4", "granularity": "month", "range": {"from": "2026-01", "to": "2026-03"}},
        "input": {
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
            }
        },
        "topWindows": [
            {
                "windowId": "cycle-1",
                "start": "2026-01-01",
                "end": "2026-01-31",
                "polarity": "supporting",
                "intensity": 0.7,
                "confidence": 0.6,
                "themes": ["window:2026-01", "structure_discipline"],
                "systemsAligned": ["western", "vedic"],
                "evidenceCycleIds": ["w1", "v1"],
            },
            {
                "windowId": "cycle-2",
                "start": "2026-02-01",
                "end": "2026-02-28",
                "polarity": "challenging",
                "intensity": 0.65,
                "confidence": 0.55,
                "themes": ["window:2026-02", "love_harmony"],
                "systemsAligned": ["chinese"],
                "evidenceCycleIds": ["c1"],
            },
        ],
        "byDomain": {"career": [], "relationships": [], "growth": []},
        "summary": [
            "Top window 2026-01-01 to 2026-01-31 (supporting, intensity 0.70, confidence 0.60) themes: structure_discipline.",
            "Most common theme across top windows: structure_discipline.",
            "Polarity balance: 1 supporting, 1 challenging, 0 neutral.",
        ],
    }

    response = build_narrative_response(forecast)

    assert response["windows"][0]["title"].startswith("Supportive window")
    assert response["windows"][1]["title"].startswith("Challenging window")
    assert response["windows"][0]["citations"]
    assert response["byDomain"]["career"]["topWindows"] == ["cycle-1"]
