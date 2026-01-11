from __future__ import annotations

from typing import Any


def enrich_windows_with_identity(
    windows: list[dict],
    convergent_profile_doc: dict,
) -> list[dict]:
    profile = _safe_dict(convergent_profile_doc.get("convergent_profile"))

    core_identity = _safe_dict(profile.get("core_operating_identity"))
    identity_label = _safe_str(core_identity.get("label"))

    tension = _safe_dict(profile.get("central_life_tension"))
    tension_axis = _safe_str(tension.get("axis"))

    shadows = _safe_list(profile.get("shadow_profile"))
    shadows = [shadow for shadow in shadows if isinstance(shadow, str)]

    strategic_alignment = _safe_dict(profile.get("strategic_alignment"))
    protective_structures = _safe_list(strategic_alignment.get("protective_structures"))
    protective_structures = [item for item in protective_structures if isinstance(item, str)]

    anti_patterns = _safe_list(strategic_alignment.get("anti_patterns"))
    anti_patterns = [item for item in anti_patterns if isinstance(item, str)]

    enriched: list[dict] = []
    for window in windows:
        if not isinstance(window, dict):
            enriched.append(window)
            continue
        window_copy = dict(window)
        title_text = _window_text(window_copy)
        tags = _classify_window_tags(title_text)
        activated_shadows = _activate_shadows(tags, shadows)
        alignment_actions = _select_alignment_actions(
            activated_shadows, protective_structures
        )

        why_text = _build_why_text(
            identity_label,
            tension_axis,
            activated_shadows,
            alignment_actions,
            anti_patterns,
        )
        takeaways = _build_takeaways(
            identity_label,
            tension_axis,
            activated_shadows,
            alignment_actions,
        )

        _apply_why(window_copy, why_text)
        _apply_takeaways(window_copy, takeaways)

        if identity_label or tension_axis or activated_shadows or alignment_actions:
            window_copy["identityContext"] = {
                "linked_identity_label": identity_label,
                "linked_tension_axis": tension_axis,
                "activated_shadows": activated_shadows,
                "alignment_actions": alignment_actions,
            }

        enriched.append(window_copy)

    return enriched


def _window_text(window: dict[str, Any]) -> str:
    for key in ("title", "topic", "headline"):
        value = window.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _classify_window_tags(title: str) -> set[str]:
    lowered = title.lower()
    tags: set[str] = set()
    if "challenging" in lowered and any(token in lowered for token in ("strength", "constraint", "capacity")):
        tags.update({"capacity_constraint", "overextension_risk"})
    if "conflict" in lowered or "relationship" in lowered:
        tags.add("conflict_pressure")
    if any(token in lowered for token in ("process", "documentation", "compliance")):
        tags.add("process_load")
    return tags


def _activate_shadows(tags: set[str], shadows: list[str]) -> list[str]:
    activated: list[str] = []
    if "overextension_risk" in tags and "Over-responsibility" in shadows:
        activated.append("Over-responsibility")
    if "conflict_pressure" in tags and "Delayed confrontation" in shadows:
        activated.append("Delayed confrontation")
    if "process_load" in tags and "Analysis paralysis" in shadows:
        activated.append("Analysis paralysis")
    if "overextension_risk" in tags and "Private emotional load" in shadows:
        activated.append("Private emotional load")
    return activated


def _select_alignment_actions(
    activated_shadows: list[str],
    protective_structures: list[str],
) -> list[str]:
    actions: list[str] = []
    preferred = set(protective_structures)

    if "Over-responsibility" in activated_shadows:
        for candidate in ("Delegation protocols", "Calendar boundaries"):
            if candidate in preferred and candidate not in actions:
                actions.append(candidate)
                if len(actions) >= 2:
                    return actions

    if "Analysis paralysis" in activated_shadows:
        candidate = "Written decision rules"
        if candidate in preferred and candidate not in actions:
            actions.append(candidate)
            if len(actions) >= 2:
                return actions

    if "Delayed confrontation" in activated_shadows:
        candidate = "Escalate early with clear consequences"
        if candidate not in actions:
            actions.append(candidate)
            if len(actions) >= 2:
                return actions

    if not actions and protective_structures:
        actions.append(protective_structures[0])

    return actions[:2]


def _build_why_text(
    identity_label: str,
    tension_axis: str,
    activated_shadows: list[str],
    alignment_actions: list[str],
    anti_patterns: list[str],
) -> str:
    label_text = identity_label or "Convergent identity"
    tension_text = tension_axis or "core tension"
    parts = [f"{label_text} lens highlights this window along {tension_text}."]

    if activated_shadows:
        parts.append(f"Activated shadows: {', '.join(activated_shadows)}.")
    if alignment_actions:
        parts.append(f"Alignment actions: {', '.join(alignment_actions)}.")
    elif anti_patterns:
        parts.append(f"Watch for anti-patterns: {', '.join(anti_patterns[:2])}.")

    return " ".join(parts)


def _build_takeaways(
    identity_label: str,
    tension_axis: str,
    activated_shadows: list[str],
    alignment_actions: list[str],
) -> list[str]:
    label_text = identity_label or "Convergent identity"
    tension_text = tension_axis or "core tension"
    takeaways = [f"Center the {label_text} perspective on {tension_text}."]

    if alignment_actions:
        takeaways.append(f"Apply {alignment_actions[0]} to stay aligned.")
        if len(alignment_actions) > 1:
            takeaways.append(f"Back it with {alignment_actions[1]}.")
    elif activated_shadows:
        takeaways.append(f"Name {activated_shadows[0]} early to avoid drift.")
    else:
        takeaways.append("Stay aligned with clear standards.")

    if activated_shadows and len(takeaways) < 3:
        takeaways.append(f"Watch for {activated_shadows[0].lower()}.")

    return takeaways[:3]


def _apply_why(window: dict[str, Any], why_text: str) -> None:
    if "why" in window:
        window["why"] = why_text
    elif "whyThisWindow" in window:
        window["whyThisWindow"] = why_text
    else:
        window["whyThisWindow"] = why_text


def _apply_takeaways(window: dict[str, Any], takeaways: list[str]) -> None:
    if "keyTakeaways" in window:
        window["keyTakeaways"] = takeaways
    elif "takeaways" in window:
        window["takeaways"] = takeaways
    else:
        window["takeaways"] = takeaways


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return value if isinstance(value, str) else ""
