import json
from pathlib import Path

import swisseph as swe

from life_chart_api.routes.profile_narrative import NarrativeRequest, get_narrative


def _normalize(payload: dict) -> dict:
    normalized = json.loads(json.dumps(payload))
    overview = normalized.get("overview", {})
    overview["citations"] = sorted(
        overview.get("citations", []), key=lambda item: item.get("windowId", "")
    )

    windows = normalized.get("windows", [])
    for window in windows:
        window["citations"] = sorted(
            window.get("citations", []), key=lambda item: item.get("windowId", "")
        )
        for citation in window.get("citations", []):
            if isinstance(citation.get("evidenceCycleIds"), list):
                citation["evidenceCycleIds"] = sorted(citation["evidenceCycleIds"])
    normalized["windows"] = sorted(windows, key=lambda item: item.get("windowId", ""))

    by_domain = normalized.get("byDomain", {})
    for domain in by_domain.values():
        if isinstance(domain.get("topWindows"), list):
            domain["topWindows"] = sorted(domain["topWindows"])
    return normalized


def test_narrative_golden_snapshot_v1():
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
        "include": "vedic,chinese",
        "granularity": "month",
        "tone": "neutral",
    }
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    model = NarrativeRequest.model_validate(params)
    response = get_narrative(model)

    fixture_path = Path(__file__).resolve().parent / "fixtures" / "narrative_golden_v1.json"
    expected = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert _normalize(response) == _normalize(expected)
