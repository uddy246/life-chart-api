from life_chart_api.temporal.vedic_dashas import build_vedic_dasha_cycles


def _lord_from_cycle(cycle: dict) -> str | None:
    for item in cycle.get("evidence", []):
        if item.get("source") == "vedic.vimshottari.lord":
            return item.get("value")
    return None


def test_vedic_dasha_builder_unit():
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

    cycles_a = build_vedic_dasha_cycles(
        birth=birth,
        range_from="1999-01",
        range_to="2030-12",
        as_of=None,
    )
    cycles_b = build_vedic_dasha_cycles(
        birth=birth,
        range_from="1999-01",
        range_to="2030-12",
        as_of=None,
    )

    assert cycles_a == cycles_b
    assert len(cycles_a) > 0

    first = cycles_a[0]
    assert _lord_from_cycle(first) in {
        "Ketu",
        "Venus",
        "Sun",
        "Moon",
        "Mars",
        "Rahu",
        "Jupiter",
        "Saturn",
        "Mercury",
    }

    sequence = None
    for item in first.get("evidence", []):
        if item.get("source") == "vedic.vimshottari.sequence":
            sequence = item.get("value")
            break
    assert sequence is not None
    assert len(sequence) == 9
