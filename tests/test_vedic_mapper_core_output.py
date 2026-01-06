from life_chart_api.astrology.vedic.mapper import map_vedic_to_core
from life_chart_api.astrology.vedic.types import VedicChartFeatures
from life_chart_api.schemas.core_output import CoreOutput


def test_map_vedic_to_core_output():
    features = VedicChartFeatures(
        lagna_sign="Capricorn",
        lagna_lord="Saturn",
        moon_sign="Taurus",
        moon_afflicted=True,
        saturn_theme="Responsibility through structure",
        rahu_ketu_emphasis=False,
        life_direction_hint="Gradual ascent through responsibility",
        timing_sensitivity_hint="medium",
        current_phase_hint="Disciplined consolidation phase",
        notes=[],
    )

    core = map_vedic_to_core(features)
    assert isinstance(core, CoreOutput)
    assert len(core.strength_patterns) <= 3
    assert len(core.friction_patterns) <= 3
    assert core.emotional_processing_style in {
        "internalised",
        "externalised",
        "cyclical",
        "suppressed",
        "expressive",
    }
    assert core.cognitive_decision_style in {
        "analytical",
        "intuitive",
        "reactive",
        "strategic",
        "deliberate",
    }
    assert core.timing_sensitivity in {
        "highly_time_sensitive",
        "moderately_cyclical",
        "relatively_stable",
    }
