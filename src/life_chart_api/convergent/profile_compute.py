from __future__ import annotations

from typing import Any

_DOMAIN_TAGS = {
    "SENSITIVITY": ["sensitivity", "empathy", "meaning_orientation", "pattern_recognition"],
    "STRUCTURE": ["structure", "duty", "discipline", "process", "standards", "institutional_navigation", "governance"],
    "DIPLOMACY": ["diplomacy", "indirect_influence", "timing", "negotiation"],
    "AUTHORITY": ["authority_through_time", "credibility_compounding", "reputation"],
    "FAIRNESS": ["fairness", "legitimacy", "ethics_first", "accountability", "standards"],
}

_LABEL_DEFINITIONS = {
    "Systemic Ethical Mediator": "Aligns fairness, process, and diplomacy to resolve complex tensions.",
    "Complexity Translator": "Bridges intuitive pattern sensing with structured interpretation.",
    "Standards Custodian": "Maintains integrity and consistency through clear standards.",
    "Institutional Strategist": "Navigates institutions to compound credibility over time.",
}

_LABEL_SUMMARIES = {
    "Systemic Ethical Mediator": "Balances ethics and systems to mediate high-stakes tradeoffs.",
    "Complexity Translator": "Turns subtle patterns into actionable structure without losing nuance.",
    "Standards Custodian": "Protects reliability by translating values into repeatable process.",
    "Institutional Strategist": "Builds enduring influence through disciplined institutional moves.",
}

_COMPETENCE_SIGNATURES = {
    "Systemic Ethical Mediator": {
        "primary_role": "Mediator",
        "secondary_role": "Standards Custodian",
        "capabilities": [
            "Cross-system fairness framing",
            "Process-driven conflict resolution",
            "Timing-sensitive negotiation",
        ],
    },
    "Complexity Translator": {
        "primary_role": "Translator",
        "secondary_role": "Systems Analyst",
        "capabilities": [
            "Pattern synthesis",
            "Structured narrative building",
            "Ambiguity reduction",
        ],
    },
    "Standards Custodian": {
        "primary_role": "Custodian",
        "secondary_role": "Process Architect",
        "capabilities": [
            "Quality standards definition",
            "Accountability scaffolding",
            "Operational discipline",
        ],
    },
    "Institutional Strategist": {
        "primary_role": "Strategist",
        "secondary_role": "Institutional Navigator",
        "capabilities": [
            "Authority compounding",
            "Reputation stewardship",
            "System-level leverage mapping",
        ],
    },
}

_INTERNAL_ENGINE_MODES = {
    "perception": {
        "empathetic": "Registers subtle emotional signals and hidden meaning.",
        "analytical": "Filters input through structured pattern recognition.",
        "contextual": "Reads nuance across stakeholders and timing.",
        "balanced": "Blends intuition with structured scanning.",
    },
    "evaluation": {
        "fairness_led": "Evaluates decisions against ethics and legitimacy.",
        "process_led": "Weights decisions by consistency and reliability.",
        "impact_led": "Optimizes for long-term authority and outcomes.",
        "values_led": "Balances meaning, fairness, and structure.",
    },
    "action": {
        "consensus": "Moves by mediation and negotiated alignment.",
        "methodical": "Executes through deliberate process steps.",
        "steady": "Builds credibility with consistent action.",
        "adaptive": "Adjusts rapidly to shifting conditions.",
    },
    "authority_building": {
        "credibility": "Compounds influence by repeated, reliable delivery.",
        "service": "Earns authority through ethics and care.",
        "consistency": "Builds standing by honoring standards over time.",
    },
}

_TENSION_TEMPLATES = {
    "Sensitivity vs Structure": {
        "description": "Balancing emotional nuance with disciplined systems.",
        "failure_expression": "Over-indexes on feeling and loses structure.",
        "maturity_expression": "Holds empathy inside clear, steady frameworks.",
    },
    "Fairness vs Authority": {
        "description": "Balancing ethical ideals with institutional constraints.",
        "failure_expression": "Avoids authority to preserve harmony.",
        "maturity_expression": "Uses authority to protect fairness.",
    },
    "Diplomacy vs Directness": {
        "description": "Balancing mediation with decisive calls.",
        "failure_expression": "Delays hard decisions to keep peace.",
        "maturity_expression": "Names truth with tact and timeliness.",
    },
    "Meaning vs Outcome": {
        "description": "Balancing purpose with measurable results.",
        "failure_expression": "Over-analyzes purpose at the expense of action.",
        "maturity_expression": "Delivers outcomes that reinforce meaning.",
    },
}

_DOMAIN_LABELS = {
    "SENSITIVITY": "sensitivity",
    "STRUCTURE": "structure",
    "DIPLOMACY": "diplomacy",
    "AUTHORITY": "authority",
    "FAIRNESS": "fairness",
}


def compute_convergent_profile(
    western: dict | None,
    vedic: dict | None,
    chinese: dict | None,
    numerology: dict | None,
) -> dict[str, Any]:
    primitives, identity_sources = build_primitives(
        western=western, vedic=vedic, chinese=chinese, numerology=numerology
    )
    tag_scores, tag_sources = aggregate_tag_scores(primitives)
    domain_scores = _compute_domain_scores(tag_scores)
    label, one_line, expanded_summary = select_core_identity_label(tag_scores, domain_scores)

    internal_engine = compute_internal_engine(domain_scores)
    tension = compute_central_life_tension(domain_scores)
    competence = compute_competence_signature(label, domain_scores)
    shadow = compute_shadow_profile(tag_scores, domain_scores)
    relationship = compute_relationship_dynamics(domain_scores, shadow)
    career = compute_career_and_power_trajectory(domain_scores)
    alignment = compute_strategic_alignment(domain_scores, shadow)
    final_statement = compute_final_convergent_statement(label, domain_scores)

    return {
        "convergent_profile": {
            "core_operating_identity": {
                "label": label,
                "one_line_definition": one_line,
                "expanded_summary": expanded_summary,
            },
            "identity_sources": identity_sources,
            "internal_engine": internal_engine,
            "central_life_tension": tension,
            "competence_signature": competence,
            "shadow_profile": shadow,
            "relationship_dynamics": relationship,
            "career_and_power_trajectory": career,
            "strategic_alignment": alignment,
            "final_convergent_statement": final_statement,
        }
    }


def build_primitives(
    *,
    western: dict | None,
    vedic: dict | None,
    chinese: dict | None,
    numerology: dict | None,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, str]]]]:
    primitives: list[dict[str, Any]] = []
    identity_sources = {"chinese": [], "vedic": [], "western": [], "numerology": []}

    def add_primitive(
        system: str,
        signal: str,
        meaning: str,
        tags: list[str],
        weight: float = 1.0,
    ) -> None:
        if not signal or not tags:
            return
        primitives.append(
            {
                "system": system,
                "signal": signal,
                "meaning": meaning,
                "tags": tags,
                "weight": weight,
            }
        )
        identity_sources[system].append({"signal": signal, "meaning": meaning})

    if isinstance(chinese, dict):
        element = _get_any(chinese, [["year", "element"], ["element"], ["yearElement"]])
        if isinstance(element, str) and element.strip():
            element_norm = element.strip().lower()
            if element_norm == "earth":
                add_primitive(
                    "chinese",
                    "Earth",
                    "Grounded, process-oriented stability.",
                    ["structure", "custodianship", "process", "credibility_compounding"],
                )

        animal = _get_any(chinese, [["year", "animal"], ["animal"], ["yearAnimal"]])
        if isinstance(animal, str) and animal.strip():
            animal_norm = animal.strip().lower()
            if animal_norm == "rabbit":
                add_primitive(
                    "chinese",
                    "Rabbit",
                    "Diplomatic, reputation-conscious influence.",
                    ["diplomacy", "institutional_navigation", "reputation", "indirect_influence"],
                )

    if isinstance(vedic, dict) and _detect_saturn_dominant(vedic):
        add_primitive(
            "vedic",
            "Saturn dominant",
            "Duty-driven structure and accountability.",
            [
                "duty",
                "structure",
                "accountability",
                "authority_through_time",
                "credibility_compounding",
                "process",
            ],
            weight=1.5,
        )

    sun_sign = None
    if isinstance(western, dict):
        sun_sign = _get_any(
            western,
            [["sunSign"], ["sun", "sign"], ["placements", "Sun", "sign"]],
        )
        if isinstance(sun_sign, str) and sun_sign.strip():
            sign_norm = sun_sign.strip().lower()
            if sign_norm == "pisces":
                add_primitive(
                    "western",
                    "Pisces Sun",
                    "Highly sensitive, meaning-oriented perception.",
                    ["sensitivity", "empathy", "meaning_orientation", "pattern_recognition"],
                )
            if sign_norm == "libra":
                add_primitive(
                    "western",
                    "Libra emphasis",
                    "Fairness-oriented diplomacy and negotiation.",
                    ["fairness", "diplomacy", "negotiation", "legitimacy"],
                )
            if sign_norm == "virgo":
                add_primitive(
                    "western",
                    "Virgo emphasis",
                    "Standards and process precision.",
                    ["standards", "process"],
                )

        if _has_sign_emphasis(western, "Libra") and (sun_sign or "").strip().lower() != "libra":
            add_primitive(
                "western",
                "Libra emphasis",
                "Fairness-oriented diplomacy and negotiation.",
                ["fairness", "diplomacy", "negotiation", "legitimacy"],
            )

        if _has_sign_emphasis(western, "Virgo") and (sun_sign or "").strip().lower() != "virgo":
            add_primitive(
                "western",
                "Virgo emphasis",
                "Standards and process precision.",
                ["standards", "process"],
            )

    if isinstance(numerology, dict):
        life_path = _get_any(numerology, [["lifePath"], ["life_path"], ["core", "lifePath"]])
        variants = _life_path_variants(life_path)
        if "11" in variants:
            add_primitive(
                "numerology",
                "Life Path 11",
                "Intuitive pattern recognition and sensitivity.",
                ["pattern_recognition", "sensitivity", "meaning_orientation"],
                weight=1.3,
            )
        if "2" in variants or "11/2" in variants:
            add_primitive(
                "numerology",
                "Life Path 2",
                "Diplomatic negotiation and fairness focus.",
                ["diplomacy", "negotiation", "fairness"],
            )

        expression = _get_any(numerology, [["expression"], ["destiny"], ["core", "expression"]])
        if isinstance(expression, (int, str)):
            expression_norm = str(expression).strip().lower()
            if expression_norm == "6":
                add_primitive(
                    "numerology",
                    "Expression 6",
                    "Ethics, standards, and custodianship.",
                    ["standards", "custodianship", "ethics_first", "accountability"],
                    weight=1.2,
                )

    return primitives, identity_sources


def aggregate_tag_scores(
    primitives: list[dict[str, Any]],
) -> tuple[dict[str, float], dict[str, set[str]]]:
    scores: dict[str, float] = {}
    sources: dict[str, set[str]] = {}
    for primitive in primitives:
        weight = float(primitive.get("weight", 1.0))
        system = primitive.get("system", "unknown")
        for tag in primitive.get("tags", []):
            scores[tag] = scores.get(tag, 0.0) + weight
            sources.setdefault(tag, set()).add(str(system))
    return scores, sources


def select_core_identity_label(
    tag_scores: dict[str, float],
    domain_scores: dict[str, float],
) -> tuple[str, str, str]:
    fairness_group = _group_score(tag_scores, ["fairness", "ethics_first", "legitimacy", "accountability"])
    process_group = _group_score(tag_scores, ["process", "institutional_navigation", "governance", "standards"])
    diplomacy_group = _group_score(tag_scores, ["diplomacy", "negotiation", "indirect_influence"])

    top_domains = _top_domains(domain_scores, count=2)

    if fairness_group >= 1.0 and process_group >= 1.0 and diplomacy_group >= 1.0:
        label = "Systemic Ethical Mediator"
    elif set(top_domains) == {"SENSITIVITY", "STRUCTURE"}:
        label = "Complexity Translator"
    elif _is_top_domain(domain_scores, "STRUCTURE") and _group_score(
        tag_scores, ["standards", "accountability", "ethics_first"]
    ) >= 1.0:
        label = "Standards Custodian"
    elif tag_scores.get("institutional_navigation", 0.0) > 0 and "AUTHORITY" in top_domains:
        label = "Institutional Strategist"
    else:
        label = _fallback_label(domain_scores)

    one_line = _LABEL_DEFINITIONS.get(label, "Integrates diverse signals into coherent guidance.")
    expanded = _LABEL_SUMMARIES.get(label, "Balances multiple systems to guide coherent action.")
    return label, one_line, expanded


def compute_internal_engine(domain_scores: dict[str, float]) -> dict[str, dict[str, str]]:
    top_domain = _top_domains(domain_scores, count=1)[0]
    secondary_domain = _top_domains(domain_scores, count=2)[1]

    perception_mode = _mode_from_domain(
        top_domain, {"SENSITIVITY": "empathetic", "STRUCTURE": "analytical", "DIPLOMACY": "contextual"}
    )
    evaluation_mode = _mode_from_domain(
        secondary_domain, {"FAIRNESS": "fairness_led", "STRUCTURE": "process_led", "AUTHORITY": "impact_led"}
    )
    action_mode = _mode_from_domain(
        top_domain, {"DIPLOMACY": "consensus", "STRUCTURE": "methodical", "AUTHORITY": "steady"}
    )
    authority_mode = _mode_from_domain(
        top_domain, {"AUTHORITY": "credibility", "FAIRNESS": "service", "SENSITIVITY": "service"}
    )

    return {
        "perception": {
            "mode": perception_mode.replace("_", " "),
            "description": _INTERNAL_ENGINE_MODES["perception"].get(perception_mode, ""),
        },
        "evaluation": {
            "mode": evaluation_mode.replace("_", " "),
            "description": _INTERNAL_ENGINE_MODES["evaluation"].get(evaluation_mode, ""),
        },
        "action": {
            "mode": action_mode.replace("_", " "),
            "description": _INTERNAL_ENGINE_MODES["action"].get(action_mode, ""),
        },
        "authority_building": {
            "mode": authority_mode.replace("_", " "),
            "description": _INTERNAL_ENGINE_MODES["authority_building"].get(authority_mode, ""),
        },
    }


def compute_central_life_tension(domain_scores: dict[str, float]) -> dict[str, str]:
    top_domains = _top_domains(domain_scores, count=2)
    if set(top_domains) == {"SENSITIVITY", "STRUCTURE"}:
        axis = "Sensitivity vs Structure"
    elif set(top_domains) == {"FAIRNESS", "AUTHORITY"}:
        axis = "Fairness vs Authority"
    elif "DIPLOMACY" in top_domains:
        axis = "Diplomacy vs Directness"
    else:
        axis = "Meaning vs Outcome"
    template = _TENSION_TEMPLATES[axis]
    return {
        "axis": axis,
        "description": template["description"],
        "failure_expression": template["failure_expression"],
        "maturity_expression": template["maturity_expression"],
    }


def compute_competence_signature(label: str, domain_scores: dict[str, float]) -> dict[str, Any]:
    if label in _COMPETENCE_SIGNATURES:
        signature = _COMPETENCE_SIGNATURES[label]
        return {
            "primary_role": signature["primary_role"],
            "secondary_role": signature["secondary_role"],
            "capabilities": list(signature["capabilities"]),
        }
    top_domains = _top_domains(domain_scores, count=2)
    return {
        "primary_role": f"{_DOMAIN_LABELS[top_domains[0]].title()} Lead",
        "secondary_role": f"{_DOMAIN_LABELS[top_domains[1]].title()} Support",
        "capabilities": [
            f"{_DOMAIN_LABELS[top_domains[0]].title()} integration",
            f"{_DOMAIN_LABELS[top_domains[1]].title()} calibration",
        ],
    }


def compute_shadow_profile(tag_scores: dict[str, float], domain_scores: dict[str, float]) -> list[str]:
    candidates = {
        "Over-responsibility": (
            tag_scores.get("duty", 0.0)
            + tag_scores.get("accountability", 0.0)
            + tag_scores.get("custodianship", 0.0)
        ),
        "Analysis paralysis": (
            tag_scores.get("pattern_recognition", 0.0)
            + tag_scores.get("standards", 0.0)
            + tag_scores.get("process", 0.0)
        ),
        "Delayed confrontation": (
            tag_scores.get("diplomacy", 0.0)
            + tag_scores.get("negotiation", 0.0)
            + tag_scores.get("fairness", 0.0)
        ),
        "Private emotional load": (
            tag_scores.get("sensitivity", 0.0)
            + tag_scores.get("empathy", 0.0)
            + tag_scores.get("meaning_orientation", 0.0)
        ),
    }
    ordered = sorted(candidates.items(), key=lambda item: (-item[1], item[0]))
    selected = [name for name, score in ordered if score > 0.5][:4]
    if len(selected) < 2 and any(score > 0 for score in candidates.values()):
        selected = [name for name, _ in ordered[:2]]
    if not selected:
        top_domain = _top_domains(domain_scores, count=1)[0]
        if top_domain == "SENSITIVITY":
            selected = ["Private emotional load", "Analysis paralysis"]
        elif top_domain == "STRUCTURE":
            selected = ["Over-responsibility", "Analysis paralysis"]
        elif top_domain == "DIPLOMACY":
            selected = ["Delayed confrontation", "Over-responsibility"]
    return selected[:4]


def compute_relationship_dynamics(domain_scores: dict[str, float], shadow_profile: list[str]) -> dict[str, Any]:
    top_domains = _top_domains(domain_scores, count=3)
    provides_map = {
        "SENSITIVITY": "empathic listening",
        "STRUCTURE": "process clarity",
        "DIPLOMACY": "conflict mediation",
        "AUTHORITY": "steady stewardship",
        "FAIRNESS": "balanced judgment",
    }
    needs_map = {
        "SENSITIVITY": "emotional reciprocity",
        "STRUCTURE": "clear roles",
        "DIPLOMACY": "time for alignment",
        "AUTHORITY": "long-term trust",
        "FAIRNESS": "ethical alignment",
    }

    naturally_provides = [provides_map[domain] for domain in top_domains[:2]]
    requires_to_thrive = [needs_map[domain] for domain in top_domains[:2]]
    common_failure_pattern = " ".join(shadow_profile[:1]) if shadow_profile else "Overextends to preserve harmony."

    return {
        "naturally_provides": naturally_provides,
        "requires_to_thrive": requires_to_thrive,
        "common_failure_pattern": common_failure_pattern,
    }


def compute_career_and_power_trajectory(domain_scores: dict[str, float]) -> dict[str, Any]:
    top_domains = _top_domains(domain_scores, count=2)
    winning_conditions = []
    if "STRUCTURE" in top_domains:
        winning_conditions.append("Clear systems and roles")
    if "FAIRNESS" in top_domains:
        winning_conditions.append("Ethical mandate")
    if "DIPLOMACY" in top_domains:
        winning_conditions.append("Multi-stakeholder alignment")
    if "AUTHORITY" in top_domains:
        winning_conditions.append("Long-term credibility")
    if not winning_conditions:
        winning_conditions = ["Consistent delivery", "Transparent standards"]

    growth_curve = "Gradual compounding through consistent stewardship."
    if "SENSITIVITY" in top_domains:
        growth_curve = "Grows influence by translating nuance into structured action."

    wealth_logic = "Value accrues through trusted, repeatable outcomes."
    if "AUTHORITY" in top_domains:
        wealth_logic = "Authority compounds as credibility grows."

    return {
        "winning_conditions": winning_conditions,
        "growth_curve": growth_curve,
        "wealth_logic": wealth_logic,
    }


def compute_strategic_alignment(domain_scores: dict[str, float], shadow_profile: list[str]) -> dict[str, Any]:
    top_domains = _top_domains(domain_scores, count=3)
    leverage_points = []
    for domain in top_domains:
        if domain == "STRUCTURE":
            leverage_points.append("Design durable systems")
        elif domain == "SENSITIVITY":
            leverage_points.append("Surface hidden patterns")
        elif domain == "DIPLOMACY":
            leverage_points.append("Negotiate shared incentives")
        elif domain == "AUTHORITY":
            leverage_points.append("Stack credibility over time")
        elif domain == "FAIRNESS":
            leverage_points.append("Set ethical guardrails")

    protective_structures = []
    if "STRUCTURE" in top_domains:
        protective_structures.append("Clear processes and checkpoints")
    if "AUTHORITY" in top_domains:
        protective_structures.append("Reputation risk monitoring")
    if not protective_structures:
        protective_structures.append("Decision review cadence")

    anti_patterns = [shadow.lower() for shadow in shadow_profile] if shadow_profile else []

    return {
        "leverage_points": leverage_points,
        "protective_structures": protective_structures,
        "anti_patterns": anti_patterns,
    }


def compute_final_convergent_statement(label: str, domain_scores: dict[str, float]) -> str:
    top_domains = _top_domains(domain_scores, count=2)
    domain_a = _DOMAIN_LABELS[top_domains[0]]
    domain_b = _DOMAIN_LABELS[top_domains[1]]
    return (
        f"As a {label}, you integrate {domain_a} and {domain_b} to deliver "
        "credible, ethical outcomes across complex systems."
    )


def _compute_domain_scores(tag_scores: dict[str, float]) -> dict[str, float]:
    scores = {}
    for domain, tags in _DOMAIN_TAGS.items():
        scores[domain] = sum(tag_scores.get(tag, 0.0) for tag in tags)
    return scores


def _top_domains(domain_scores: dict[str, float], count: int) -> list[str]:
    ordered = sorted(domain_scores.items(), key=lambda item: (-item[1], item[0]))
    return [domain for domain, _ in ordered[:count]]


def _is_top_domain(domain_scores: dict[str, float], domain: str) -> bool:
    return _top_domains(domain_scores, count=1)[0] == domain


def _group_score(tag_scores: dict[str, float], tags: list[str]) -> float:
    return sum(tag_scores.get(tag, 0.0) for tag in tags)


def _fallback_label(domain_scores: dict[str, float]) -> str:
    top_domain = _top_domains(domain_scores, count=1)[0]
    if top_domain == "STRUCTURE":
        return "Standards Custodian"
    if top_domain == "AUTHORITY":
        return "Institutional Strategist"
    if top_domain == "DIPLOMACY":
        return "Systemic Ethical Mediator"
    return "Complexity Translator"


def _mode_from_domain(domain: str, mapping: dict[str, str]) -> str:
    return mapping.get(domain, "balanced")


def _get_any(data: dict[str, Any], paths: list[list[str]]) -> Any:
    for path in paths:
        value: Any = data
        for key in path:
            if not isinstance(value, dict) or key not in value:
                value = None
                break
            value = value[key]
        if value is not None:
            return value
    return None


def _detect_saturn_dominant(vedic: dict[str, Any]) -> bool:
    dominant = _extract_list_strings(vedic.get("dominantPlanets"))
    if any(item.lower() == "saturn" for item in dominant):
        return True
    themes = _extract_list_strings(vedic.get("themes"))
    if any(item.lower() == "saturn" for item in themes):
        return True
    flags = vedic.get("flags", {})
    if isinstance(flags, dict) and flags.get("saturnDominant") is True:
        return True
    summary = vedic.get("summary")
    return isinstance(summary, str) and "saturn" in summary.lower()


def _has_sign_emphasis(western: dict[str, Any], sign: str) -> bool:
    sign_lower = sign.lower()
    for key in ["dominantSigns", "signs", "themes", "emphasis"]:
        for item in _extract_list_strings(western.get(key)):
            if sign_lower in item.lower():
                return True
    summary = western.get("summary")
    if isinstance(summary, str) and sign_lower in summary.lower():
        return True
    return False


def _extract_list_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, str):
        return [value]
    return []


def _life_path_variants(value: Any) -> set[str]:
    if isinstance(value, (int, float)):
        return {str(int(value))}
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return set()
        parts = [part.strip() for part in stripped.split("/") if part.strip()]
        variants = {stripped}
        variants.update(parts)
        return variants
    return set()
