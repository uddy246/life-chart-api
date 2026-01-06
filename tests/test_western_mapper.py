from life_chart_api.astrology.western.mapper import map_western_to_core
from life_chart_api.astrology.western.types import WesternChartFeatures


def test_map_western_to_core_shapes():
    features = WesternChartFeatures(
        sun_sign="Aries",
        moon_sign="Cancer",
        ascendant_sign="Libra",
        dominant_element=None,
        dominant_modality=None,
        mercury_style=None,
        mars_style="Hesitant-then-committed",
        venus_style="Independence-preserving",
        saturn_theme="Responsibility through structure",
        notes=[],
    )

    core = map_western_to_core(features)
    assert len(core.strength_patterns) <= 3
    assert len(core.friction_patterns) <= 3
