from life_chart_api.narrative.deep_reading import synthesize_deep_reading
from life_chart_api.main import app
from tests.asgi_client import call_app


def test_deep_reading_deterministic_fallback():
    convergent_profile_doc = _udbhav_like_profile()
    windows = _sample_windows()
    response = synthesize_deep_reading(convergent_profile_doc, windows, tone="neutral", enable_llm=False)

    assert response.get("summary")
    assert "TODO" not in response.get("summary", "")

    sections = response.get("sections", [])
    assert len(sections) == 6
    expected_titles = [
        "Core Operating Identity",
        "Internal Engine",
        "Central Life Tension",
        "Shadows and Failure Modes",
        "This Period’s Through-Line",
        "Strategic Recommendations",
    ]
    assert [section.get("title") for section in sections] == expected_titles
    for section in sections:
        body = section.get("body", "")
        assert body
        assert "TODO" not in body


def test_deep_reading_determinism():
    convergent_profile_doc = _udbhav_like_profile()
    windows = _sample_windows()
    response_a = synthesize_deep_reading(convergent_profile_doc, windows, tone="direct", enable_llm=False)
    response_b = synthesize_deep_reading(convergent_profile_doc, windows, tone="direct", enable_llm=False)
    assert response_a == response_b


def test_deep_reading_llm_fallback_when_unavailable():
    convergent_profile_doc = _udbhav_like_profile()
    windows = _sample_windows()
    response = synthesize_deep_reading(convergent_profile_doc, windows, tone="neutral", enable_llm=True)
    assert response.get("summary")
    sections = response.get("sections", [])
    assert len(sections) == 6


def test_deep_reading_wiring_in_profile_narrative():
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
        "tone": "neutral",
    }
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    assert isinstance(payload, dict)
    assert "profile" in payload
    narrative = payload.get("narrative", {})
    assert isinstance(narrative, dict)
    deep_reading = narrative.get("deepReading")
    assert isinstance(deep_reading, dict)
    assert isinstance(deep_reading.get("summary"), str)
    assert isinstance(deep_reading.get("sections"), list)


def _udbhav_like_profile() -> dict:
    return {
        "convergent_profile": {
            "core_operating_identity": {
                "label": "Systemic Ethical Mediator",
                "one_line_definition": "Aligns fairness with process.",
                "expanded_summary": "Balances ethics and institutions.",
            },
            "internal_engine": {
                "perception": {"mode": "empathetic", "description": "Reads nuance."},
                "evaluation": {"mode": "fairness led", "description": "Weights legitimacy."},
                "action": {"mode": "consensus", "description": "Builds alignment."},
                "authority_building": {"mode": "credibility", "description": "Compounds trust."},
            },
            "central_life_tension": {
                "axis": "Sensitivity vs Structure",
                "description": "Balances nuance with structure.",
                "failure_expression": "Over-indexes on feeling.",
                "maturity_expression": "Holds empathy inside systems.",
            },
            "competence_signature": {
                "primary_role": "Mediator",
                "secondary_role": "Standards Custodian",
                "capabilities": ["Process clarity"],
            },
            "shadow_profile": ["Over-responsibility", "Delayed confrontation"],
            "strategic_alignment": {
                "leverage_points": ["Set ethical guardrails"],
                "protective_structures": ["Delegation protocols", "Calendar boundaries"],
                "anti_patterns": ["over-responsibility"],
            },
        }
    }


def _sample_windows() -> list[dict]:
    return [
        {
            "title": "Challenging window: day master strength",
            "whyThisWindow": "Capacity is tested; avoid overextension.",
            "takeaways": ["Hold boundaries", "Delegate early"],
            "identityContext": {
                "linked_identity_label": "Systemic Ethical Mediator",
                "linked_tension_axis": "Sensitivity vs Structure",
                "activated_shadows": ["Over-responsibility"],
                "alignment_actions": ["Delegation protocols"],
            },
            "confidence": 0.7,
            "intensity": 0.8,
        },
        {
            "title": "Supportive window for growth",
            "takeaways": ["Reinforce structure"],
            "identityContext": {
                "linked_identity_label": "Systemic Ethical Mediator",
                "linked_tension_axis": "Sensitivity vs Structure",
                "activated_shadows": [],
                "alignment_actions": ["Calendar boundaries"],
            },
            "confidence": 0.6,
            "intensity": 0.5,
        },
    ]
