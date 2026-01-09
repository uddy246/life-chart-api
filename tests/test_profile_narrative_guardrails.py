from __future__ import annotations

from life_chart_api.routes.profile_forecast import ForecastRequest, get_forecast
from life_chart_api.routes.profile_narrative import NarrativeRequest, get_narrative


def _get_narrative(params: dict) -> dict:
    model = NarrativeRequest.model_validate(params)
    return get_narrative(model)


def _get_forecast(params: dict) -> dict:
    model = ForecastRequest.model_validate(params)
    return get_forecast(model)


def _collect_strings(payload: dict) -> list[str]:
    texts: list[str] = []
    overview = payload.get("overview", {})
    texts.append(overview.get("headline", ""))
    texts.extend(overview.get("bullets", []))

    for window in payload.get("windows", []):
        texts.append(window.get("title", ""))
        texts.extend(window.get("paragraphs", []))
        texts.extend(window.get("takeaways", []))

    by_domain = payload.get("byDomain", {})
    for domain in ("career", "relationships", "growth"):
        block = by_domain.get(domain, {})
        texts.append(block.get("headline", ""))
        texts.extend(block.get("bullets", []))
    return [text for text in texts if isinstance(text, str)]


def _assert_citation(citation: dict) -> None:
    window_id = citation.get("windowId")
    themes = citation.get("themes", [])
    systems = citation.get("systemsAligned", [])
    evidence_ids = citation.get("evidenceCycleIds", [])
    assert isinstance(window_id, str) and window_id
    assert isinstance(themes, list) and len(themes) >= 1
    assert isinstance(systems, list) and len(systems) >= 1
    assert isinstance(evidence_ids, list)
    assert evidence_ids == sorted(evidence_ids)
    if systems:
        assert evidence_ids


def test_profile_narrative_guardrails():
    params = {
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

    banned = [
        "you will",
        "guaranteed",
        "definitely",
        "promise",
        "will happen",
        "going to happen",
    ]
    for tone in ("neutral", "direct", "reflective"):
        tone_params = dict(params)
        tone_params["tone"] = tone
        narrative = _get_narrative(tone_params)

        for text in _collect_strings(narrative):
            lowered = text.lower()
            assert not any(phrase in lowered for phrase in banned)

        overview = narrative.get("overview", {})
        for citation in overview.get("citations", []):
            _assert_citation(citation)

        for window in narrative.get("windows", []):
            for citation in window.get("citations", []):
                _assert_citation(citation)

        forecast_params = dict(tone_params)
        forecast_params.pop("tone", None)
        forecast = _get_forecast(forecast_params)
        forecast_ids = [window.get("windowId") for window in forecast.get("topWindows", [])]
        narrative_ids = [window.get("windowId") for window in narrative.get("windows", [])]
        assert narrative_ids == forecast_ids
