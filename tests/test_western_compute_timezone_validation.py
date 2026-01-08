import pytest

from life_chart_api.astrology.western.compute import compute_western_features


def test_compute_western_features_invalid_timezone():
    with pytest.raises(ValueError, match="Invalid timezone:"):
        compute_western_features(
            date="1999-02-26",
            time="14:00:00",
            tz="Not/AZone",
            lat=17.385,
            lon=78.4867,
        )
