from __future__ import annotations

import json
from typing import Any

_SYSTEM_PROMPT = (
    "You are a narrative assistant. You may only use the provided JSON facts. "
    "Do not introduce new placements, predictions, or claims. "
    "If information is missing, say: 'Not specified in the profile data.' "
    "Output must be valid JSON with keys: summary, sections, safety."
)

_USER_PROMPT_TEMPLATE = (
    "Tone: {tone}\n"
    "Convergent Profile (JSON):\n{profile_json}\n"
    "Enriched Windows (JSON):\n{windows_json}\n"
    "Return JSON with:\n"
    "- summary: string\n"
    "- sections: array of 6 objects with title and body\n"
    "- safety: object with constraintsApplied and groundingMode\n"
)

_SECTION_TITLES = [
    "Core Operating Identity",
    "Internal Engine",
    "Central Life Tension",
    "Shadows and Failure Modes",
    "This Period’s Through-Line",
    "Strategic Recommendations",
]


class LLMClient:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError("LLM client is not configured.")


def synthesize_deep_reading(
    convergent_profile_doc: dict,
    enriched_windows: list[dict],
    tone: str = "neutral",
    enable_llm: bool = False,
) -> dict[str, Any]:
    if enable_llm:
        llm_output = _attempt_llm(convergent_profile_doc, enriched_windows, tone)
        if llm_output is not None:
            return llm_output
    return _deterministic_deep_reading(convergent_profile_doc, enriched_windows, tone)


def _attempt_llm(
    convergent_profile_doc: dict,
    enriched_windows: list[dict],
    tone: str,
) -> dict[str, Any] | None:
    client = LLMClient()
    payload = _build_llm_payload(convergent_profile_doc, enriched_windows, tone)
    try:
        response = client.generate(payload["system_prompt"], payload["user_prompt"])
    except Exception:
        return None
    try:
        parsed = json.loads(response)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    if "summary" not in parsed or "sections" not in parsed or "safety" not in parsed:
        return None
    return parsed


def _build_llm_payload(
    convergent_profile_doc: dict,
    enriched_windows: list[dict],
    tone: str,
) -> dict[str, str]:
    profile_json = json.dumps(convergent_profile_doc, ensure_ascii=True, indent=2)
    windows_json = json.dumps(enriched_windows, ensure_ascii=True, indent=2)
    user_prompt = _USER_PROMPT_TEMPLATE.format(
        tone=tone,
        profile_json=profile_json,
        windows_json=windows_json,
    )
    return {"system_prompt": _SYSTEM_PROMPT, "user_prompt": user_prompt}


def _deterministic_deep_reading(
    convergent_profile_doc: dict,
    enriched_windows: list[dict],
    tone: str,
) -> dict[str, Any]:
    profile = _safe_dict(convergent_profile_doc.get("convergent_profile"))
    core = _safe_dict(profile.get("core_operating_identity"))
    internal_engine = _safe_dict(profile.get("internal_engine"))
    tension = _safe_dict(profile.get("central_life_tension"))
    competence = _safe_dict(profile.get("competence_signature"))
    shadows = _safe_list(profile.get("shadow_profile"))
    strategic = _safe_dict(profile.get("strategic_alignment"))

    label = _safe_str(core.get("label"))
    one_line = _safe_str(core.get("one_line_definition"))
    expanded = _safe_str(core.get("expanded_summary"))
    axis = _safe_str(tension.get("axis"))
    description = _safe_str(tension.get("description"))
    failure = _safe_str(tension.get("failure_expression"))
    maturity = _safe_str(tension.get("maturity_expression"))
    primary_role = _safe_str(competence.get("primary_role"))
    secondary_role = _safe_str(competence.get("secondary_role"))
    protective_structures = _safe_list(strategic.get("protective_structures"))
    leverage_points = _safe_list(strategic.get("leverage_points"))
    anti_patterns = _safe_list(strategic.get("anti_patterns"))
    activated_shadows = _collect_activated_shadows(enriched_windows)

    summary = _build_summary(label, axis, enriched_windows, tone)

    sections = [
        {"title": _SECTION_TITLES[0], "body": _core_identity_body(label, one_line, expanded)},
        {
            "title": _SECTION_TITLES[1],
            "body": _internal_engine_body(internal_engine),
        },
        {
            "title": _SECTION_TITLES[2],
            "body": _tension_body(axis, description, failure, maturity),
        },
        {
            "title": _SECTION_TITLES[3],
            "body": _shadows_body(shadows, failure),
        },
        {
            "title": _SECTION_TITLES[4],
            "body": _through_line_body(enriched_windows, label, axis),
        },
        {
            "title": _SECTION_TITLES[5],
            "body": _strategy_body(
                leverage_points,
                protective_structures,
                anti_patterns,
                activated_shadows,
                primary_role,
                secondary_role,
            ),
        },
    ]

    return {
        "summary": summary,
        "sections": sections,
        "safety": {"constraintsApplied": True, "groundingMode": "profile+windows-only"},
    }


def _build_summary(label: str, axis: str, windows: list[dict], tone: str) -> str:
    label_text = label or "Convergent identity"
    axis_text = axis or "core tension"
    window_count = len([window for window in windows if isinstance(window, dict)])
    if tone == "direct":
        return f"{label_text} read: balance {axis_text}. {window_count} windows inform this guidance."
    if tone == "reflective":
        return f"{label_text} reflects on {axis_text}. {window_count} windows inform the thread."
    return f"{label_text} balances {axis_text}. {window_count} windows ground this reading."


def _core_identity_body(label: str, one_line: str, expanded: str) -> str:
    if not any([label, one_line, expanded]):
        return "Not specified in the profile data."
    parts = [label, one_line, expanded]
    return " ".join(part for part in parts if part)


def _internal_engine_body(internal_engine: dict[str, Any]) -> str:
    if not internal_engine:
        return "Not specified in the profile data."
    pieces = []
    for key in ("perception", "evaluation", "action", "authority_building"):
        entry = _safe_dict(internal_engine.get(key))
        mode = _safe_str(entry.get("mode"))
        description = _safe_str(entry.get("description"))
        if not mode and not description:
            continue
        label = key.replace("_", " ").title()
        if description:
            pieces.append(f"{label}: {mode} — {description}".strip(" —"))
        else:
            pieces.append(f"{label}: {mode}")
    return " ".join(pieces) if pieces else "Not specified in the profile data."


def _tension_body(axis: str, description: str, failure: str, maturity: str) -> str:
    if not any([axis, description, failure, maturity]):
        return "Not specified in the profile data."
    parts = []
    if axis:
        parts.append(f"Axis: {axis}.")
    if description:
        parts.append(description)
    if failure:
        parts.append(f"Failure mode: {failure}.")
    if maturity:
        parts.append(f"Maturity expression: {maturity}.")
    return " ".join(parts)


def _shadows_body(shadows: list[Any], failure: str) -> str:
    shadow_names = [shadow for shadow in shadows if isinstance(shadow, str)]
    if not shadow_names and not failure:
        return "Not specified in the profile data."
    parts = []
    if shadow_names:
        parts.append(f"Shadows: {', '.join(shadow_names[:4])}.")
    if failure:
        parts.append(f"Common failure pattern: {failure}.")
    return " ".join(parts)


def _through_line_body(windows: list[dict], label: str, axis: str) -> str:
    selected = _select_windows(windows)
    if not selected:
        return "Not specified in the profile data."
    parts = []
    for window in selected:
        title = _safe_str(window.get("title"))
        why = _safe_str(window.get("whyThisWindow")) or _safe_str(window.get("why"))
        takeaway = ""
        if not why:
            takeaways = _safe_list(window.get("takeaways"))
            for item in takeaways:
                if isinstance(item, str) and item:
                    takeaway = item
                    break
        detail = why or takeaway
        if title and detail:
            parts.append(f"{title}: {detail}")
        elif title:
            parts.append(title)
    header = ""
    if label or axis:
        header = f"{label or 'Convergent identity'} along {axis or 'core tension'}."
    return " ".join([item for item in [header, " ".join(parts)] if item]).strip()


def _strategy_body(
    leverage_points: list[Any],
    protective_structures: list[Any],
    anti_patterns: list[Any],
    activated_shadows: list[str],
    primary_role: str,
    secondary_role: str,
) -> str:
    parts = []
    roles = " / ".join([role for role in [primary_role, secondary_role] if role])
    if roles:
        parts.append(f"Competence signature: {roles}.")
    leverage = [item for item in leverage_points if isinstance(item, str)]
    protective = [item for item in protective_structures if isinstance(item, str)]
    patterns = [item for item in anti_patterns if isinstance(item, str)]
    if leverage:
        parts.append(f"Leverage points: {', '.join(leverage[:3])}.")
    if protective:
        parts.append(f"Protective structures: {', '.join(protective[:3])}.")
    if activated_shadows:
        parts.append(f"Activated shadows to watch: {', '.join(activated_shadows[:3])}.")
    if patterns:
        parts.append(f"Anti-patterns: {', '.join(patterns[:3])}.")
    return " ".join(parts) if parts else "Not specified in the profile data."


def _select_windows(windows: list[dict]) -> list[dict]:
    scored = []
    for idx, window in enumerate(windows):
        if not isinstance(window, dict):
            continue
        confidence = _coerce_float(window.get("confidence"))
        intensity = _coerce_float(window.get("intensity"))
        scored.append((idx, confidence, intensity, window))
    has_scores = any(confidence > 0 or intensity > 0 for _, confidence, intensity, _ in scored)
    if has_scores:
        scored.sort(key=lambda item: (-item[2], -item[1], item[0]))
    else:
        scored.sort(key=lambda item: item[0])
    return [item[3] for item in scored[:3]]


def _collect_activated_shadows(windows: list[dict]) -> list[str]:
    activated: list[str] = []
    for window in windows:
        if not isinstance(window, dict):
            continue
        identity_context = window.get("identityContext", {})
        if not isinstance(identity_context, dict):
            continue
        shadows = identity_context.get("activated_shadows", [])
        if isinstance(shadows, list):
            for shadow in shadows:
                if isinstance(shadow, str) and shadow not in activated:
                    activated.append(shadow)
    return activated


def _coerce_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return value if isinstance(value, str) else ""
