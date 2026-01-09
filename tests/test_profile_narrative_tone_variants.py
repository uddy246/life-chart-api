from life_chart_api.routes.profile_narrative import NarrativeRequest, get_narrative


def _get_narrative(params: dict) -> dict:
    model = NarrativeRequest.model_validate(params)
    return get_narrative(model)


def test_profile_narrative_tone_variants():
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

    neutral = _get_narrative({**base, "tone": "neutral"})
    direct = _get_narrative({**base, "tone": "direct"})

    neutral_ids = [window.get("windowId") for window in neutral.get("windows", [])]
    direct_ids = [window.get("windowId") for window in direct.get("windows", [])]
    assert neutral_ids == direct_ids

    neutral_citations = neutral.get("overview", {}).get("citations", [])
    direct_citations = direct.get("overview", {}).get("citations", [])
    assert neutral_citations == direct_citations

    neutral_titles = [window.get("title") for window in neutral.get("windows", [])]
    direct_titles = [window.get("title") for window in direct.get("windows", [])]
    assert neutral_titles != direct_titles
