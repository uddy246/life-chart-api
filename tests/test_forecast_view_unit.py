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


def test_forecast_view_ui_diversity_and_continuation():
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
            "themes": ["window:2026-01", "day_master_strength", "element_earth"],
            "start": "2026-01-01",
            "end": "2026-01-31",
            "intensity": 0.9,
            "confidence": 0.8,
            "polarity": "supporting",
            "evidence": [
                {
                    "source": "timeline.cycle",
                    "value": {"system": "chinese", "cycleId": "c1"},
                    "weight": 0.5,
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
            "themes": ["window:2026-02", "day_master_strength", "learning_growth"],
            "start": "2026-02-01",
            "end": "2026-02-28",
            "intensity": 0.85,
            "confidence": 0.79,
            "polarity": "supporting",
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
        {
            "cycleId": "cycle-3",
            "system": "intersection",
            "kind": "window",
            "domain": "growth",
            "themes": ["window:2026-03", "love_harmony"],
            "start": "2026-03-01",
            "end": "2026-03-31",
            "intensity": 0.7,
            "confidence": 0.78,
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
    ]

    response = build_forecast_response(
        name=None,
        birth=birth,
        range_from="2026-01",
        range_to="2026-03",
        granularity="month",
        as_of=None,
        intersection_cycles=cycles,
        top_n=2,
    )

    top_windows = response["topWindows"]
    primary_themes = [window.get("ui", {}).get("primaryTheme") for window in top_windows]
    assert len(set(primary_themes)) >= 2

    repeated_cycles = [
        {
            "cycleId": "cycle-4",
            "system": "intersection",
            "kind": "window",
            "domain": "growth",
            "themes": ["window:2026-04", "structure_discipline", "learning_growth"],
            "start": "2026-04-01",
            "end": "2026-04-30",
            "intensity": 0.8,
            "confidence": 0.75,
            "polarity": "supporting",
            "evidence": [
                {
                    "source": "timeline.cycle",
                    "value": {"system": "western", "cycleId": "w2"},
                    "weight": 0.4,
                    "note": "test",
                }
            ],
            "notes": [],
        },
        {
            "cycleId": "cycle-5",
            "system": "intersection",
            "kind": "window",
            "domain": "growth",
            "themes": ["window:2026-05", "structure_discipline", "pressure_maturation"],
            "start": "2026-05-01",
            "end": "2026-05-31",
            "intensity": 0.78,
            "confidence": 0.74,
            "polarity": "supporting",
            "evidence": [
                {
                    "source": "timeline.cycle",
                    "value": {"system": "vedic", "cycleId": "v2"},
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
        range_from="2026-04",
        range_to="2026-05",
        granularity="month",
        as_of=None,
        intersection_cycles=repeated_cycles,
        top_n=2,
    )

    top_windows = response["topWindows"]
    assert top_windows[1].get("ui", {}).get("isContinuation") is True
    display = top_windows[1].get("ui", {}).get("displayThemes", [])
    primary = top_windows[1].get("ui", {}).get("primaryTheme")
    if isinstance(display, list) and len(display) > 1:
        assert display[0] != primary
