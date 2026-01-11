import json
from pathlib import Path


def _assert_keys(obj: dict, expected: list[str], context: str) -> None:
    missing = [key for key in expected if key not in obj]
    extra = [key for key in obj if key not in expected]
    assert not missing, f"{context} missing keys: {missing}"
    assert not extra, f"{context} unexpected keys: {extra}"


def _assert_type(value, expected_type, context: str) -> None:
    assert isinstance(value, expected_type), (
        f"{context} expected {expected_type.__name__}, got {type(value).__name__}"
    )


def test_convergent_profile_schema_scaffold():
    schema_path = Path(__file__).resolve().parents[1] / "docs" / "convergent_profile.schema.json"
    assert schema_path.exists(), "docs/convergent_profile.schema.json is missing"

    data = json.loads(schema_path.read_text(encoding="utf-8"))
    assert set(data.keys()) == {"convergent_profile"}, "top-level keys must be {'convergent_profile'}"

    profile = data["convergent_profile"]
    _assert_type(profile, dict, "convergent_profile")
    _assert_keys(
        profile,
        [
            "core_operating_identity",
            "identity_sources",
            "internal_engine",
            "central_life_tension",
            "competence_signature",
            "shadow_profile",
            "relationship_dynamics",
            "career_and_power_trajectory",
            "strategic_alignment",
            "final_convergent_statement",
        ],
        "convergent_profile",
    )

    core = profile["core_operating_identity"]
    _assert_type(core, dict, "core_operating_identity")
    _assert_keys(core, ["label", "one_line_definition", "expanded_summary"], "core_operating_identity")
    assert core["label"] == ""
    assert core["one_line_definition"] == ""
    assert core["expanded_summary"] == ""

    sources = profile["identity_sources"]
    _assert_type(sources, dict, "identity_sources")
    _assert_keys(sources, ["chinese", "vedic", "western", "numerology"], "identity_sources")
    for key in ["chinese", "vedic", "western", "numerology"]:
        _assert_type(sources[key], list, f"identity_sources.{key}")
        assert sources[key] == []

    engine = profile["internal_engine"]
    _assert_type(engine, dict, "internal_engine")
    _assert_keys(engine, ["perception", "evaluation", "action", "authority_building"], "internal_engine")
    for key in ["perception", "evaluation", "action", "authority_building"]:
        mode = engine[key]
        _assert_type(mode, dict, f"internal_engine.{key}")
        _assert_keys(mode, ["mode", "description"], f"internal_engine.{key}")
        assert mode["mode"] == ""
        assert mode["description"] == ""

    tension = profile["central_life_tension"]
    _assert_type(tension, dict, "central_life_tension")
    _assert_keys(
        tension,
        ["axis", "description", "failure_expression", "maturity_expression"],
        "central_life_tension",
    )
    assert tension["axis"] == ""
    assert tension["description"] == ""
    assert tension["failure_expression"] == ""
    assert tension["maturity_expression"] == ""

    signature = profile["competence_signature"]
    _assert_type(signature, dict, "competence_signature")
    _assert_keys(signature, ["primary_role", "secondary_role", "capabilities"], "competence_signature")
    assert signature["primary_role"] == ""
    assert signature["secondary_role"] == ""
    _assert_type(signature["capabilities"], list, "competence_signature.capabilities")
    assert signature["capabilities"] == []

    _assert_type(profile["shadow_profile"], list, "shadow_profile")
    assert profile["shadow_profile"] == []

    relationship = profile["relationship_dynamics"]
    _assert_type(relationship, dict, "relationship_dynamics")
    _assert_keys(
        relationship,
        ["naturally_provides", "requires_to_thrive", "common_failure_pattern"],
        "relationship_dynamics",
    )
    _assert_type(relationship["naturally_provides"], list, "relationship_dynamics.naturally_provides")
    _assert_type(relationship["requires_to_thrive"], list, "relationship_dynamics.requires_to_thrive")
    assert relationship["naturally_provides"] == []
    assert relationship["requires_to_thrive"] == []
    assert relationship["common_failure_pattern"] == ""

    career = profile["career_and_power_trajectory"]
    _assert_type(career, dict, "career_and_power_trajectory")
    _assert_keys(career, ["winning_conditions", "growth_curve", "wealth_logic"], "career_and_power_trajectory")
    _assert_type(career["winning_conditions"], list, "career_and_power_trajectory.winning_conditions")
    assert career["winning_conditions"] == []
    assert career["growth_curve"] == ""
    assert career["wealth_logic"] == ""

    alignment = profile["strategic_alignment"]
    _assert_type(alignment, dict, "strategic_alignment")
    _assert_keys(
        alignment,
        ["leverage_points", "protective_structures", "anti_patterns"],
        "strategic_alignment",
    )
    _assert_type(alignment["leverage_points"], list, "strategic_alignment.leverage_points")
    _assert_type(alignment["protective_structures"], list, "strategic_alignment.protective_structures")
    _assert_type(alignment["anti_patterns"], list, "strategic_alignment.anti_patterns")
    assert alignment["leverage_points"] == []
    assert alignment["protective_structures"] == []
    assert alignment["anti_patterns"] == []

    assert profile["final_convergent_statement"] == ""
