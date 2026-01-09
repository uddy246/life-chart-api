from __future__ import annotations

from datetime import date
from typing import Any

from life_chart_api.temporal.models import clamp01, normalize_iso_ym, sort_cycles, stable_id


def _pillar_label(pillar: dict[str, Any]) -> str:
    stem = pillar.get("stem")
    branch = pillar.get("branch")
    if isinstance(stem, str) and isinstance(branch, str):
        return f"{stem}-{branch}"
    return "unknown"


def _pillar_element(pillar: dict[str, Any]) -> str | None:
    element = pillar.get("stemElement")
    if isinstance(element, str):
        return element
    return None


def _overlaps(start: str, end: str, range_from: str, range_to: str) -> bool:
    return start <= range_to and end >= range_from


def build_chinese_luck_pillar_cycles(
    *,
    chinese_system_output: dict[str, Any],
    range_from: str,
    range_to: str,
    as_of: str | None = None,
) -> list[dict[str, Any]]:
    range_from_norm = normalize_iso_ym(range_from)
    range_to_norm = normalize_iso_ym(range_to)

    birth = chinese_system_output.get("input", {}).get("birth", {})
    birth_date = birth.get("date")
    birth_year = None
    if isinstance(birth_date, str) and len(birth_date) >= 4:
        try:
            birth_year = date.fromisoformat(birth_date).year
        except ValueError:
            birth_year = None

    luck_cycles = chinese_system_output.get("luckCycles", {})
    pillars = luck_cycles.get("pillars") if isinstance(luck_cycles, dict) else None
    if not isinstance(pillars, list):
        return []

    favourable = chinese_system_output.get("elements", {}).get("favourable", [])
    unfavourable = chinese_system_output.get("elements", {}).get("unfavourable", [])
    dm_strength = chinese_system_output.get("dayMaster", {}).get("strength")

    cycles: list[dict[str, Any]] = []
    for pillar_entry in pillars:
        if not isinstance(pillar_entry, dict):
            continue
        pillar = pillar_entry.get("pillar", {})
        if not isinstance(pillar, dict):
            continue
        label = _pillar_label(pillar)
        element = _pillar_element(pillar)

        start_age = pillar_entry.get("startAge")
        end_age = pillar_entry.get("endAge")
        approx = False
        if birth_year is not None and isinstance(start_age, (int, float)) and isinstance(
            end_age, (int, float)
        ):
            start_year = birth_year + int(start_age)
            end_year = birth_year + int(end_age)
            start_str = f"{start_year:04d}-01"
            end_str = f"{end_year:04d}-01"
        else:
            approx = True
            start_str = range_from_norm
            end_str = range_to_norm

        if not _overlaps(start_str, end_str, range_from_norm, range_to_norm):
            continue

        if element in favourable:
            intensity = 0.7
            polarity = "supporting"
        elif element in unfavourable:
            intensity = 0.75
            polarity = "challenging"
        else:
            intensity = 0.5
            polarity = "neutral"

        themes = [f"pillar:{label}"]
        if element:
            themes.append(f"element:{element}")
        if isinstance(dm_strength, str):
            themes.append(f"dm:{dm_strength}")

        evidence_note = "Luck pillar from Chinese Tier 2."
        if approx:
            evidence_note = "Approx: placeholder range used."

        cycles.append(
            {
                "cycleId": stable_id(["chinese", "luck_pillar", label, start_str, end_str]),
                "system": "chinese",
                "kind": "luck_pillar",
                "domain": "growth",
                "themes": themes,
                "start": start_str,
                "end": end_str,
                "intensity": clamp01(intensity),
                "polarity": polarity,
                "evidence": [
                    {
                        "source": "chinese.luck_pillars",
                        "value": {
                            "label": label,
                            "startAge": start_age,
                            "endAge": end_age,
                            "element": element,
                        },
                        "weight": 0.7,
                        "note": evidence_note,
                    }
                ],
                "notes": ["approx"] if approx else [],
            }
        )

    return sort_cycles(cycles)
