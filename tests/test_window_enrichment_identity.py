from life_chart_api.convergent.window_enrichment import enrich_windows_with_identity


def test_window_enrichment_identity_udbhav_like():
    convergent_profile_doc = _udbhav_like_profile()
    windows = [{"title": "Challenging window: day master strength", "takeaways": ["old"]}]

    enriched = enrich_windows_with_identity(windows, convergent_profile_doc)
    assert enriched is not windows
    enriched_window = enriched[0]

    why_text = enriched_window.get("whyThisWindow") or enriched_window.get("why", "")
    assert "Systemic Ethical Mediator" in why_text
    assert "Sensitivity vs Structure" in why_text

    identity_context = enriched_window.get("identityContext", {})
    activated = identity_context.get("activated_shadows", [])
    assert "Over-responsibility" in activated

    takeaways = enriched_window.get("takeaways", [])
    assert any(
        action in " ".join(takeaways)
        for action in ("Delegation protocols", "Calendar boundaries", "Written decision rules")
    )

    enriched_again = enrich_windows_with_identity(windows, convergent_profile_doc)
    assert enriched == enriched_again


def _udbhav_like_profile() -> dict:
    return {
        "convergent_profile": {
            "core_operating_identity": {"label": "Systemic Ethical Mediator"},
            "central_life_tension": {"axis": "Sensitivity vs Structure"},
            "shadow_profile": ["Over-responsibility", "Delayed confrontation", "Private emotional load"],
            "strategic_alignment": {
                "protective_structures": [
                    "Written decision rules",
                    "Calendar boundaries",
                    "Delegation protocols",
                ],
                "anti_patterns": ["over-responsibility", "delayed confrontation"],
            },
        }
    }
