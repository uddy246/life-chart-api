from __future__ import annotations

from typing import Any, Iterable

from life_chart_api.synthesis.signal_extractors import (
    Signal,
    extract_chinese_signals,
    extract_numerology_signals,
    extract_vedic_signals,
    extract_western_signals,
)

_SYSTEM_ORDER = ("western", "vedic", "chinese", "numerology")


def _ordered_systems(systems: Iterable[str]) -> list[str]:
    system_set = set(systems)
    return [system for system in _SYSTEM_ORDER if system in system_set]


def _build_evidence(signals: list[Signal]) -> list[dict[str, Any]]:
    evidence = []
    for signal in signals:
        evidence.append(
            {"system": signal.system, "key": signal.evidence_key, "note": signal.note}
        )
    return evidence


def build_intersection(profile_response: dict[str, Any]) -> dict[str, Any]:
    systems = profile_response.get("systems", {})
    western = systems.get("western", {}) if isinstance(systems, dict) else {}
    vedic = systems.get("vedic", {}) if isinstance(systems, dict) else {}
    chinese = systems.get("chinese", {}) if isinstance(systems, dict) else {}
    numerology = systems.get("numerology") if isinstance(systems, dict) else None

    signals = []
    signals.extend(extract_western_signals(western))
    signals.extend(extract_vedic_signals(vedic))
    signals.extend(extract_chinese_signals(chinese))
    signals.extend(extract_numerology_signals(numerology))

    by_tag: dict[str, list[Signal]] = {}
    for signal in signals:
        by_tag.setdefault(signal.tag, []).append(signal)

    convergences: list[dict[str, Any]] = []
    divergences: list[dict[str, Any]] = []
    tag_weights: dict[str, float] = {}

    for tag, tag_signals in sorted(by_tag.items(), key=lambda item: item[0]):
        if len(tag_signals) < 2:
            continue
        total_weight = sum(signal.weight for signal in tag_signals)
        tag_weights[tag] = total_weight
        polarity_sum = sum(signal.polarity * signal.weight for signal in tag_signals)
        if polarity_sum > 0:
            dominant_sign = 1
        elif polarity_sum < 0:
            dominant_sign = -1
        else:
            dominant_sign = 0
        matching = sum(1 for signal in tag_signals if signal.polarity == dominant_sign)
        agreement = dominant_sign != 0 and matching >= (len(tag_signals) + 1) // 2

        systems_list = _ordered_systems([signal.system for signal in tag_signals])
        evidence = _build_evidence(sorted(tag_signals, key=lambda s: (s.system, s.tag)))

        if agreement:
            avg_weight = total_weight / len(tag_signals)
            confidence = min(1.0, 0.35 + 0.15 * (len(tag_signals) - 2) + avg_weight * 0.35)
            convergences.append(
                {
                    "systems": systems_list,
                    "signal": f"Shared emphasis on {tag}",
                    "confidence": round(confidence, 2),
                    "note": f"Multiple systems align on {tag}.",
                    "evidence": evidence,
                }
            )
        else:
            divergences.append(
                {
                    "systems": systems_list,
                    "signal": f"Mixed signals for {tag}",
                    "note": f"Systems disagree on {tag}.",
                    "evidence": evidence,
                }
            )

    bridge_tags = [
        tag
        for tag, _ in sorted(
            tag_weights.items(), key=lambda item: (-item[1], item[0])
        )
    ][:5]

    if convergences:
        headline = "Convergences highlight " + ", ".join(
            [entry["signal"] for entry in convergences[:2]]
        )
    else:
        headline = "No strong cross-system convergences detected yet."

    notes = [
        f"Convergences: {len(convergences)}; divergences: {len(divergences)}.",
        f"Bridge tags: {', '.join(bridge_tags) if bridge_tags else 'none'}.",
    ]
    next_actions = [
        "Replace template narratives with computed interpretations.",
        "Enable timing-based intersection rules.",
        "Add numerology schema.",
    ]

    return {
        "convergences": convergences,
        "divergences": divergences,
        "bridgeTags": bridge_tags,
        "summary": {"headline": headline, "notes": notes, "nextActions": next_actions},
    }
