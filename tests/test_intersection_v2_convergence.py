from life_chart_api.synthesis.intersection_engine_v2 import build_intersection_v2


def test_intersection_v2_convergence():
    systems = {
        "western": {
            "planets": [
                {"planet": "saturn", "sign": "capricorn"},
            ],
            "identity": {
                "sunSign": {"sign": "capricorn"},
                "moonSign": {"sign": "taurus"},
                "ascendant": {"sign": "capricorn"},
            },
        },
        "chinese": {
            "elements": {"favourable": ["metal"]},
            "tenGods": {"dominant": ["directOfficer"]},
            "dayMaster": {"strength": "strong", "element": "metal"},
        },
        "numerology": {
            "primitives": {"life_path": {"reduction": {"final_value": 4}}},
        },
        "vedic": {},
    }

    result = build_intersection_v2({"systems": systems})
    convergences = result.get("convergences", [])
    assert any(entry.get("id") == "structure_discipline" for entry in convergences)
    entry = next(item for item in convergences if item.get("id") == "structure_discipline")
    assert entry.get("confidence", 0) > 0.3
    systems_list = entry.get("systems", [])
    assert "western" in systems_list
    assert "chinese" in systems_list
