from life_chart_api.convergent.profile_compute import compute_convergent_profile


def _assert_keys(obj: dict, expected: list[str], context: str) -> None:
    missing = [key for key in expected if key not in obj]
    extra = [key for key in obj if key not in expected]
    assert not missing, f"{context} missing keys: {missing}"
    assert not extra, f"{context} unexpected keys: {extra}"


def test_convergent_profile_compute_schema_conformance():
    response = compute_convergent_profile(None, None, None, None)
    assert set(response.keys()) == {"convergent_profile"}

    profile = response["convergent_profile"]
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
    _assert_keys(core, ["label", "one_line_definition", "expanded_summary"], "core_operating_identity")
    assert isinstance(core["label"], str)
    assert isinstance(core["one_line_definition"], str)
    assert isinstance(core["expanded_summary"], str)

    sources = profile["identity_sources"]
    _assert_keys(sources, ["chinese", "vedic", "western", "numerology"], "identity_sources")
    for key in ["chinese", "vedic", "western", "numerology"]:
        assert isinstance(sources[key], list)
        for item in sources[key]:
            assert isinstance(item, dict)
            _assert_keys(item, ["signal", "meaning"], f"identity_sources.{key}")

    engine = profile["internal_engine"]
    _assert_keys(engine, ["perception", "evaluation", "action", "authority_building"], "internal_engine")
    for key in ["perception", "evaluation", "action", "authority_building"]:
        entry = engine[key]
        _assert_keys(entry, ["mode", "description"], f"internal_engine.{key}")
        assert isinstance(entry["mode"], str)
        assert isinstance(entry["description"], str)

    tension = profile["central_life_tension"]
    _assert_keys(
        tension,
        ["axis", "description", "failure_expression", "maturity_expression"],
        "central_life_tension",
    )
    assert isinstance(tension["axis"], str)
    assert isinstance(tension["description"], str)
    assert isinstance(tension["failure_expression"], str)
    assert isinstance(tension["maturity_expression"], str)

    competence = profile["competence_signature"]
    _assert_keys(competence, ["primary_role", "secondary_role", "capabilities"], "competence_signature")
    assert isinstance(competence["primary_role"], str)
    assert isinstance(competence["secondary_role"], str)
    assert isinstance(competence["capabilities"], list)

    assert isinstance(profile["shadow_profile"], list)

    relationship = profile["relationship_dynamics"]
    _assert_keys(
        relationship,
        ["naturally_provides", "requires_to_thrive", "common_failure_pattern"],
        "relationship_dynamics",
    )
    assert isinstance(relationship["naturally_provides"], list)
    assert isinstance(relationship["requires_to_thrive"], list)
    assert isinstance(relationship["common_failure_pattern"], str)

    career = profile["career_and_power_trajectory"]
    _assert_keys(career, ["winning_conditions", "growth_curve", "wealth_logic"], "career_and_power_trajectory")
    assert isinstance(career["winning_conditions"], list)
    assert isinstance(career["growth_curve"], str)
    assert isinstance(career["wealth_logic"], str)

    alignment = profile["strategic_alignment"]
    _assert_keys(
        alignment,
        ["leverage_points", "protective_structures", "anti_patterns"],
        "strategic_alignment",
    )
    assert isinstance(alignment["leverage_points"], list)
    assert isinstance(alignment["protective_structures"], list)
    assert isinstance(alignment["anti_patterns"], list)

    assert isinstance(profile["final_convergent_statement"], str)


def test_convergent_profile_compute_deterministic():
    inputs = _udbhav_like_fixture()
    response_a = compute_convergent_profile(**inputs)
    response_b = compute_convergent_profile(**inputs)
    assert response_a == response_b


def test_convergent_profile_udbhav_like_fixture():
    inputs = _udbhav_like_fixture()
    response = compute_convergent_profile(**inputs)
    profile = response["convergent_profile"]
    assert profile["core_operating_identity"]["label"] == "Systemic Ethical Mediator"
    assert profile["central_life_tension"]["axis"] == "Sensitivity vs Structure"
    assert 2 <= len(profile["shadow_profile"]) <= 4


def _udbhav_like_fixture() -> dict:
    return {
        "chinese": {"element": "Earth", "animal": "Rabbit"},
        "vedic": {"flags": {"saturnDominant": True}},
        "western": {"sunSign": "Pisces"},
        "numerology": {"lifePath": "11/2", "expression": "6"},
    }
