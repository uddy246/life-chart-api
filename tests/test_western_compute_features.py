from life_chart_api.astrology.western.compute import compute_western_features


def test_compute_western_features_shape():
    features = compute_western_features(
        date="1999-02-26",
        time="14:00:00",
        tz="Asia/Kolkata",
        lat=17.385,
        lon=78.4867,
    )

    valid_signs = {
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    }
    assert features.sun_sign in valid_signs
    assert features.moon_sign in valid_signs
    assert features.ascendant_sign in valid_signs

    assert features.dominant_element in {None, "Fire", "Earth", "Air", "Water"}
    assert features.dominant_modality in {None, "Cardinal", "Fixed", "Mutable"}
    assert isinstance(features.notes, list)
