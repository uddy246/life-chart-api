from life_chart_api.temporal.temporal_intersection import build_temporal_intersection_cycles


def test_temporal_intersection_builder_emits_window():
    cycles = [
        {
            "cycleId": "cycle-vedic-1",
            "system": "vedic",
            "kind": "dasha_maha",
            "domain": "growth",
            "themes": ["discipline", "responsibility"],
            "start": "2026-01",
            "end": "2026-12",
            "intensity": 0.7,
            "polarity": "supporting",
            "evidence": [],
        },
        {
            "cycleId": "cycle-western-1",
            "system": "western",
            "kind": "return_saturn",
            "domain": "growth",
            "themes": ["structure", "saturn_return"],
            "start": "2026-01",
            "end": "2026-04",
            "intensity": 0.65,
            "polarity": "supporting",
            "evidence": [],
        },
    ]

    windows = build_temporal_intersection_cycles(
        cycles,
        range_from="2026-01",
        range_to="2026-03",
        granularity="month",
    )

    assert windows
    window = windows[0]
    assert window["system"] == "intersection"
    assert "structure_discipline" in window.get("themes", [])
    evidence_ids = {entry.get("value", {}).get("cycleId") for entry in window.get("evidence", [])}
    assert "cycle-vedic-1" in evidence_ids
    assert "cycle-western-1" in evidence_ids


def test_temporal_intersection_adjacent_windows_not_identical():
    cycles = [
        {
            "cycleId": "cycle-western-short",
            "system": "western",
            "kind": "return_saturn",
            "domain": "growth",
            "themes": ["discipline"],
            "start": "2026-01-01",
            "end": "2026-01-10",
            "intensity": 0.8,
            "polarity": "supporting",
            "evidence": [],
        },
        {
            "cycleId": "cycle-vedic-span",
            "system": "vedic",
            "kind": "dasha_maha",
            "domain": "growth",
            "themes": ["pressure"],
            "start": "2026-01-20",
            "end": "2026-02-05",
            "intensity": 0.6,
            "polarity": "challenging",
            "evidence": [],
        },
        {
            "cycleId": "cycle-chinese-short",
            "system": "chinese",
            "kind": "yearly",
            "domain": "growth",
            "themes": ["growth"],
            "start": "2026-02-10",
            "end": "2026-02-28",
            "intensity": 0.7,
            "polarity": "supporting",
            "evidence": [],
        },
    ]

    windows = build_temporal_intersection_cycles(
        cycles,
        range_from="2026-01",
        range_to="2026-02",
        granularity="month",
    )

    assert len(windows) >= 2
    signatures = {
        (
            tuple(
                sorted(
                    theme
                    for theme in window.get("themes", [])
                    if isinstance(theme, str) and not theme.startswith("window:")
                )
            ),
            round(float(window.get("intensity", 0.0)), 4),
            round(float(window.get("confidence", 0.0)), 4),
            window.get("polarity"),
        )
        for window in windows
    }
    assert len(signatures) > 1
