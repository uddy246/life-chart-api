from __future__ import annotations

from typing import Any

from life_chart_api.temporal.models import normalize_iso_ym, sort_cycles, stable_id


def build_timeline_scaffold(
    *,
    name: str | None,
    birth: dict[str, Any],
    range_from: str,
    range_to: str,
) -> dict[str, Any]:
    start = normalize_iso_ym(range_from)
    end = normalize_iso_ym(range_to)

    cycles = []
    for system in ("western", "vedic", "chinese", "numerology"):
        cycle = {
            "cycleId": stable_id([system, "scaffold", start, end]),
            "system": system,
            "kind": "scaffold",
            "domain": "growth",
            "themes": ["scaffold"],
            "start": start,
            "end": end,
            "intensity": 0.0,
            "polarity": "neutral",
            "evidence": [
                {
                    "source": f"{system}.scaffold",
                    "value": "phase2.1",
                    "weight": 0.0,
                    "note": "Scaffold placeholder.",
                }
            ],
            "notes": ["scaffold"],
        }
        cycles.append(cycle)

    cycles = sort_cycles(cycles)

    response = {
        "meta": {"version": "phase2.1"},
        "input": {"birth": birth},
        "range": {"from": start, "to": end},
        "cycles": cycles,
    }
    if name:
        response["input"]["name"] = name
    return response
