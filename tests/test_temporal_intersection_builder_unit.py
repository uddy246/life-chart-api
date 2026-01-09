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
