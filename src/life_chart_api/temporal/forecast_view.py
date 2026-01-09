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
    return {
        "windowId": _window_id(cycle),
        "start": cycle.get("start"),
        "end": cycle.get("end"),
        "polarity": cycle.get("polarity"),
        "intensity": float(cycle.get("intensity", 0.0)),
        "confidence": _compute_confidence(cycle),
        "themes": themes,
        "systemsAligned": systems,
        "evidenceCycleIds": evidence_ids,
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
    themes = _clean_themes(top.get("themes", []))
    theme_text = ", ".join(themes[:3]) if themes else "general growth"
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
    top_windows = summaries[:top_n]

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
    if name:
        response["input"]["name"] = name
    if as_of:
        response["meta"]["as_of"] = as_of
    return response
