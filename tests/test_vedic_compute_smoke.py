from life_chart_api.astrology.vedic.compute import compute_vedic_features
from life_chart_api.astrology.vedic.mapper import map_vedic_to_core
from life_chart_api.astrology.vedic.types import VedicChartFeatures
from life_chart_api.schemas.core_output import CoreOutput


def test_compute_vedic_features_smoke():
    features = compute_vedic_features(
        date="1990-01-01",
        time="12:00",
        tz="UTC",
        lat=28.6139,
        lon=77.2090,
    )

    assert isinstance(features, VedicChartFeatures)
    assert features.lagna_sign
    assert features.lagna_lord
    assert features.moon_sign

    core = map_vedic_to_core(features)
    assert isinstance(core, CoreOutput)
    assert core.core_identity_theme
    assert core.emotional_processing_style
    assert core.core_identity_theme.startswith(features.lagna_sign)
