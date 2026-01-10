from life_chart_api.engines.intersection_engine import build_intersection_report, extract_signals


def test_intersection_engine_v1_overlap():
    profile = {
        "systems": {
            "numerology": {
                "primitives": {"life_path": {"reduction": {"final_value": 1}}}
            },
            "western": {
                "strengths": {
                    "chartBalance": {
                        "elements": {"high": ["fire"]},
                        "modalities": {"high": []},
                    }
                }
            },
            "vedic": {"moon_sign": "Aries"},
        }
    }

    signals = extract_signals(profile)
    report = build_intersection_report(signals)

    assert report.version == "intersection_v1"
    assert any(finding.theme_id == "initiative" for finding in report.overlaps)
