from life_chart_api.routes.profile_narrative import NarrativeRequest, get_narrative


def _get_narrative(params: dict) -> dict:
    model = NarrativeRequest.model_validate(params)
    return get_narrative(model)


def test_profile_narrative_tone_deterministic():
    base = {
        "name": "Example Person",
        "date": "1999-02-26",
        "time": "14:00:00",
        "timezone": "UTC",
        "city": "Hyderabad",
        "region": "Telangana",
        "country": "India",
        "lat": 17.385,
        "lon": 78.4867,
        "from": "2026-01",
        "to": "2027-12",
        "include": "western,vedic,chinese",
        "granularity": "month",
    }

    for tone in ("neutral", "direct", "reflective"):
        params = dict(base)
        params["tone"] = tone
        response_a = _get_narrative(params)
        response_b = _get_narrative(params)
        assert response_a == response_b
