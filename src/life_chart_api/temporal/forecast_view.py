from __future__ import annotations

from collections import Counter
from typing import Any

from life_chart_api.temporal.models import clamp01

_CAREER_TAGS = {"structure_discipline", "authority", "ambition", "responsibility", "pressure_maturation"}
_RELATIONSHIP_TAGS = {"love_harmony", "relationships", "belonging"}


def _systems_aligned(cycle: dict[str, Any]) -> list[str]:
    systems = set()
    for entry in cycle.get("evidence", []):
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if isinstance(value, dict):
            system = value.get("system")
            if isinstance(system, str):
                systems.add(system)
    return sorted(systems)


def _evidence_cycle_ids(cycle: dict[str, Any]) -> list[str]:
    ids = set()
    for entry in cycle.get("evidence", []):
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if isinstance(value, dict):
            cycle_id = value.get("cycleId")
            if isinstance(cycle_id, str):
                ids.add(cycle_id)
    return sorted(ids)


def _window_id(cycle: dict[str, Any]) -> str:
    cycle_id = cycle.get("cycleId")
    return cycle_id if isinstance(cycle_id, str) else "unknown"


def _clean_themes(themes: list[str]) -> list[str]:
    cleaned = []
    for theme in themes:
        if not isinstance(theme, str):
            continue
        if theme.startswith("window:"):
            continue
        cleaned.append(theme)
    return cleaned


def _base_ui(themes: list[str]) -> dict[str, Any]:
    cleaned = _clean_themes(themes)
    primary = cleaned[0] if cleaned else "general_growth"
    display = cleaned[:] if cleaned else [primary]
    return {"primaryTheme": primary, "displayThemes": display, "isContinuation": False}


def _promote_secondary(display: list[str], primary: str) -> list[str]:
    for idx, theme in enumerate(display):
        if theme != primary:
            if idx == 0:
                return list(display)
            reordered = [theme]
            for j, item in enumerate(display):
                if j != idx:
                    reordered.append(item)
            return reordered
    return list(display)


def _apply_ui_continuation(windows: list[dict[str, Any]]) -> None:
    prev_primary: str | None = None
    for window in windows:
        ui = window.get("ui")
        if not isinstance(ui, dict):
            ui = _base_ui(window.get("themes", []))
        primary = ui.get("primaryTheme")
        if not isinstance(primary, str) or not primary:
            primary = "general_growth"
            ui["primaryTheme"] = primary
        display = ui.get("displayThemes")
        if not isinstance(display, list) or not display:
            display = [primary]
        is_continuation = prev_primary == primary if prev_primary else False
        ui["isContinuation"] = is_continuation
        if is_continuation:
            display = _promote_secondary(display, primary)
        ui["displayThemes"] = display
        window["ui"] = ui
        prev_primary = primary


def _select_top_windows(summaries: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    if top_n <= 0:
        return []
    selected: list[dict[str, Any]] = []
    selected_ids: set[int] = set()
    seen_themes: set[str] = set()

    for window in summaries:
        ui = window.get("ui", {})
        primary = ui.get("primaryTheme", "general_growth")
        if isinstance(primary, str) and primary not in seen_themes:
            selected.append(window)
            selected_ids.add(id(window))
            seen_themes.add(primary)
            if len(selected) >= top_n:
                return selected

    for window in summaries:
        if id(window) in selected_ids:
            continue
        selected.append(window)
        if len(selected) >= top_n:
            break
    return selected


def _compute_confidence(cycle: dict[str, Any]) -> float:
    systems = _systems_aligned(cycle)
    systems_factor = min(1.0, len(systems) / 3.0)
    intensity_factor = clamp01(float(cycle.get("intensity", 0.0)))
    confidence = clamp01(0.55 * systems_factor + 0.45 * intensity_factor)
    return round(confidence, 2)


def summarize_window(cycle: dict[str, Any]) -> dict[str, Any]:
    themes = list(cycle.get("themes", []))
    systems = _systems_aligned(cycle)
    evidence_ids = _evidence_cycle_ids(cycle)
    ui = _base_ui(themes)
    confidence = cycle.get("confidence")
    if isinstance(confidence, (int, float)):
        confidence_value = round(clamp01(float(confidence)), 2)
    else:
        confidence_value = _compute_confidence(cycle)
    return {
        "windowId": _window_id(cycle),
        "start": cycle.get("start"),
        "end": cycle.get("end"),
        "polarity": cycle.get("polarity"),
        "intensity": float(cycle.get("intensity", 0.0)),
        "confidence": confidence_value,
        "themes": themes,
        "systemsAligned": systems,
        "evidenceCycleIds": evidence_ids,
        "ui": ui,
    }


def assign_domain(themes: list[str]) -> str:
    theme_set = set(_clean_themes(themes))
    if theme_set & _CAREER_TAGS:
        return "career"
    if theme_set & _RELATIONSHIP_TAGS:
        return "relationships"
    return "growth"


def _sort_key(window: dict[str, Any]) -> tuple:
    return (
        -float(window.get("confidence", 0.0)),
        -float(window.get("intensity", 0.0)),
        str(window.get("start", "")),
        str(window.get("windowId", "")),
    )


def build_summary_bullets(top_windows: list[dict[str, Any]], range_from: str, range_to: str) -> list[str]:
    if not top_windows:
        return [
            "No high-confidence windows in selected range.",
            f"Range covers {range_from} to {range_to}.",
            "No dominant themes detected in the top windows.",
        ]

    top = top_windows[0]
    ui = top.get("ui", {}) if isinstance(top.get("ui"), dict) else {}
    display_themes = ui.get("displayThemes")
    if not isinstance(display_themes, list) or not display_themes:
        display_themes = _clean_themes(top.get("themes", []))
    if not display_themes:
        display_themes = ["general_growth"]
    theme_text = ", ".join(display_themes[:3])
    if ui.get("isContinuation"):
        bullets = [
            (
                f"Continuation: {top.get('start')} to {top.get('end')} "
                f"({top.get('polarity')}, intensity {top.get('intensity'):.2f}, "
                f"confidence {top.get('confidence'):.2f})."
            ),
        ]
    else:
        bullets = [
            (
                f"Top window {top.get('start')} to {top.get('end')} "
                f"({top.get('polarity')}, intensity {top.get('intensity'):.2f}, "
                f"confidence {top.get('confidence'):.2f}) themes: {theme_text}."
            ),
        ]

    all_themes: list[str] = []
    for window in top_windows:
        all_themes.extend(_clean_themes(window.get("themes", [])))
    if all_themes:
        most_common, _ = Counter(all_themes).most_common(1)[0]
        bullets.append(f"Most common theme across top windows: {most_common}.")

    polarity_counts = Counter(window.get("polarity") for window in top_windows)
    bullets.append(
        "Polarity balance: "
        f"{polarity_counts.get('supporting', 0)} supporting, "
        f"{polarity_counts.get('challenging', 0)} challenging, "
        f"{polarity_counts.get('neutral', 0)} neutral."
    )

    return bullets


def build_forecast_response(
    *,
    name: str | None,
    birth: dict[str, Any],
    range_from: str,
    range_to: str,
    granularity: str,
    as_of: str | None,
    intersection_cycles: list[dict[str, Any]],
    top_n: int = 6,
) -> dict[str, Any]:
    granularity = "quarter" if granularity == "quarter" else "month"
    summaries = [summarize_window(cycle) for cycle in intersection_cycles]
    summaries.sort(key=_sort_key)
    top_windows = _select_top_windows(summaries, top_n)
    _apply_ui_continuation(top_windows)

    by_domain = {
        "career": [],
        "relationships": [],
        "growth": [],
        "personality": [],
        "mind": [],
        "energy": [],
        "health": [],
        "money": [],
    }
    for window in summaries:
        domain = assign_domain(window.get("themes", []))
        by_domain[domain].append(window)

    summary = build_summary_bullets(top_windows, range_from, range_to)

    response = {
        "meta": {
            "version": "phase2.4",
            "granularity": granularity,
            "range": {"from": range_from, "to": range_to},
        },
        "input": {"birth": birth},
        "topWindows": top_windows,
        "byDomain": by_domain,
        "summary": summary,
    }
    # TEMPORARY: frontend compatibility shim for legacy fields.
    response["overview"] = response["summary"]
    response["windows"] = response["topWindows"]
    if name:
        response["input"]["name"] = name
    if as_of:
        response["meta"]["as_of"] = as_of
    return response
