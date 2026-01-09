from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Any

from life_chart_api.temporal.models import clamp01, normalize_iso_ym, stable_id

_SYSTEM_WEIGHTS = {
    "western": 0.30,
    "vedic": 0.35,
    "chinese": 0.25,
    "numerology": 0.10,
}

_THEME_KEYWORDS = {
    "structure_discipline": {"discipline", "responsibility", "structure", "saturn_return", "saturn_transit"},
    "expansion_growth": {"growth", "expansion", "guidance", "jupiter_return"},
    "volatility_ambition": {"disruption", "ambition"},
    "love_harmony": {"relationships", "comfort", "belonging"},
    "pressure_maturation": {"pressure", "constraint"},
    "learning_growth": {"learning", "trade"},
    "spiritual_reflection": {"spirituality", "detachment"},
    "emotional_depth": {"emotions"},
    "drive_assertion": {"drive", "conflict"},
}

_ELEMENT_TAGS = {"wood", "fire", "earth", "metal", "water"}


def _parse_date(value: str, *, end: bool) -> date:
    if len(value) == 7:
        year, month = map(int, value.split("-"))
        day = monthrange(year, month)[1] if end else 1
        return date(year, month, day)
    if len(value) == 10:
        year, month, day = map(int, value.split("-"))
        return date(year, month, day)
    normalized = normalize_iso_ym(value)
    year, month = map(int, normalized.split("-"))
    day = monthrange(year, month)[1] if end else 1
    return date(year, month, day)


def _month_start(dt: date) -> date:
    return date(dt.year, dt.month, 1)


def _month_end(dt: date) -> date:
    return date(dt.year, dt.month, monthrange(dt.year, dt.month)[1])


def _quarter_start(dt: date) -> date:
    quarter = (dt.month - 1) // 3
    month = quarter * 3 + 1
    return date(dt.year, month, 1)


def _quarter_end(dt: date) -> date:
    start = _quarter_start(dt)
    end_month = start.month + 2
    return date(start.year, end_month, monthrange(start.year, end_month)[1])


def _add_months(start: date, months: int) -> date:
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    return date(year, month, 1)


def _iter_windows(range_from: str, range_to: str, granularity: str) -> list[dict[str, Any]]:
    range_start = _month_start(_parse_date(range_from, end=False))
    range_end = _month_end(_parse_date(range_to, end=True))
    windows: list[dict[str, Any]] = []

    if granularity == "quarter":
        current = _quarter_start(range_start)
        while current <= range_end:
            start = _quarter_start(current)
            end = _quarter_end(current)
            window_id = f"{start.year}-Q{((start.month - 1) // 3) + 1}"
            if end >= range_start and start <= range_end:
                windows.append(
                    {
                        "id": window_id,
                        "start": start,
                        "end": end,
                    }
                )
            current = _add_months(current, 3)
    else:
        current = _month_start(range_start)
        while current <= range_end:
            start = current
            end = _month_end(current)
            window_id = start.strftime("%Y-%m")
            windows.append({"id": window_id, "start": start, "end": end})
            current = _add_months(current, 1)

    return windows


def normalize_time_themes(cycle: dict[str, Any]) -> set[str]:
    themes = cycle.get("themes", [])
    normalized: set[str] = set()
    for raw in themes:
        if not isinstance(raw, str):
            continue
        lower = raw.lower()
        if lower.startswith("element:"):
            element = lower.split(":", 1)[1].strip()
            if element in _ELEMENT_TAGS:
                normalized.add(f"element_{element}")
            continue
        if lower.startswith("pillar:"):
            normalized.add("pillar_cycle")
            continue
        if lower.startswith("dm:"):
            normalized.add("day_master_strength")
            continue
        for tag, keywords in _THEME_KEYWORDS.items():
            if lower in keywords:
                normalized.add(tag)
    return normalized


def build_temporal_intersection_cycles(
    all_cycles: list[dict[str, Any]],
    range_from: str,
    range_to: str,
    granularity: str = "month",
) -> list[dict[str, Any]]:
    granularity = "quarter" if granularity == "quarter" else "month"
    windows = _iter_windows(range_from, range_to, granularity)
    intersection_cycles: list[dict[str, Any]] = []

    for window in windows:
        window_start = window["start"]
        window_end = window["end"]
        window_id = window["id"]

        overlapping: list[dict[str, Any]] = []
        for cycle in all_cycles:
            start_raw = cycle.get("start")
            end_raw = cycle.get("end")
            if not isinstance(start_raw, str) or not isinstance(end_raw, str):
                continue
            cycle_start = _parse_date(start_raw, end=False)
            cycle_end = _parse_date(end_raw, end=True)
            if cycle_start <= window_end and cycle_end >= window_start:
                overlapping.append(cycle)

        if not overlapping:
            continue

        theme_scores: dict[str, float] = {}
        theme_support: dict[str, float] = {}
        theme_challenge: dict[str, float] = {}
        theme_support_systems: dict[str, set[str]] = {}
        theme_challenge_systems: dict[str, set[str]] = {}
        systems_present: set[str] = set()
        weighted_cycles: list[tuple[dict[str, Any], float, int]] = []

        for cycle in overlapping:
            system = cycle.get("system")
            if system not in _SYSTEM_WEIGHTS:
                continue
            intensity = float(cycle.get("intensity", 0.0))
            weight = _SYSTEM_WEIGHTS[system] * intensity
            polarity = cycle.get("polarity", "neutral")
            sign = 0
            if polarity == "supporting":
                sign = 1
            elif polarity == "challenging":
                sign = -1

            if weight <= 0.0:
                continue

            systems_present.add(system)
            weighted_cycles.append((cycle, weight, sign))

            for theme in normalize_time_themes(cycle):
                theme_scores[theme] = theme_scores.get(theme, 0.0) + weight * sign
                if sign > 0:
                    theme_support[theme] = theme_support.get(theme, 0.0) + weight
                    theme_support_systems.setdefault(theme, set())
                    if weight >= 0.15:
                        theme_support_systems[theme].add(system)
                elif sign < 0:
                    theme_challenge[theme] = theme_challenge.get(theme, 0.0) + weight
                    theme_challenge_systems.setdefault(theme, set())
                    if weight >= 0.15:
                        theme_challenge_systems[theme].add(system)

        if not weighted_cycles:
            continue

        convergences: list[str] = []
        divergences: list[str] = []
        for theme, score in theme_scores.items():
            support_systems = theme_support_systems.get(theme, set())
            if len(support_systems) >= 2 and score > 0.10:
                convergences.append(theme)
            support_weight = theme_support.get(theme, 0.0)
            challenge_weight = theme_challenge.get(theme, 0.0)
            if support_weight >= 0.20 and challenge_weight >= 0.20:
                divergences.append(theme)

        total_weight = sum(weight for _, weight, _ in weighted_cycles)
        net = sum(weight * sign for _, weight, sign in weighted_cycles)
        magnitude = clamp01(total_weight)
        intensity = clamp01(0.5 * magnitude + 0.5 * abs(net))
        if net > 0.10:
            polarity = "supporting"
        elif net < -0.10:
            polarity = "challenging"
        else:
            polarity = "neutral"

        if not convergences and not divergences and magnitude < 0.20:
            continue

        def _theme_sort_key(theme: str) -> tuple[float, str]:
            return (-(theme_support.get(theme, 0.0)), theme)

        top_themes = sorted(convergences, key=_theme_sort_key)
        if not top_themes and theme_scores:
            top_themes = sorted(
                theme_scores.keys(),
                key=lambda t: (-abs(theme_scores.get(t, 0.0)), t),
            )
        top_themes = top_themes[:3]

        themes = [f"window:{window_id}"]
        themes.extend(sorted(set(top_themes)))
        if divergences:
            themes.append("tension")

        systems_count = len(systems_present)
        total_conflicts = len(divergences)
        total_alignments = len(convergences)
        agreement = 1.0 - min(1.0, total_conflicts / max(1, total_alignments + total_conflicts))
        confidence = clamp01((systems_count / 3.0) * 0.6 + agreement * 0.4)

        evidence = []
        for cycle, weight, sign in weighted_cycles:
            evidence.append(
                {
                    "source": "timeline.cycle",
                    "value": {
                        "system": cycle.get("system"),
                        "cycleId": cycle.get("cycleId"),
                        "kind": cycle.get("kind"),
                        "themes": cycle.get("themes", []),
                        "polarity": cycle.get("polarity"),
                        "intensity": cycle.get("intensity"),
                    },
                    "weight": clamp01(weight),
                    "note": f"contribution={'+' if sign > 0 else '-' if sign < 0 else '0'}{weight:.2f}; confidence={confidence:.2f}",
                }
            )
        evidence.sort(key=lambda item: (item["value"].get("system", ""), item["value"].get("cycleId", "")))

        start_str = window_start.strftime("%Y-%m-%d")
        end_str = window_end.strftime("%Y-%m-%d")
        intersection_cycles.append(
            {
                "cycleId": stable_id(["intersection", "window", window_id, granularity]),
                "system": "intersection",
                "kind": "window",
                "domain": "growth",
                "themes": themes,
                "start": start_str,
                "end": end_str,
                "intensity": intensity,
                "polarity": polarity,
                "evidence": evidence,
                "notes": [],
            }
        )

    return intersection_cycles
