from __future__ import annotations

from typing import Any

from life_chart_api.synthesis.signal_extractors_v2 import CanonicalSignal, extract_signals_v2

_BASELINE_WEIGHTS = {
    "western": 0.30,
    "vedic": 0.30,
    "chinese": 0.25,
    "numerology": 0.15,
}

_SYSTEM_ORDER = ("western", "vedic", "chinese", "numerology")


def _ordered_systems(systems: list[str]) -> list[str]:
    system_set = set(systems)
    return [system for system in _SYSTEM_ORDER if system in system_set]


def _system_weights(signals: list[CanonicalSignal]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for signal in signals:
        evidence = signal.evidence[0]
        weights[evidence.system] = max(weights.get(evidence.system, 0.0), evidence.weight)
    return weights


def _evidence_list(signals: list[CanonicalSignal]) -> list[dict[str, Any]]:
    evidence_items = []
    for signal in signals:
        for evidence in signal.evidence:
            evidence_items.append(
                {
                    "system": evidence.system,
                    "weight": evidence.weight,
                    "source": evidence.source,
                    "value": evidence.value,
                    "note": evidence.note,
                }
            )
    return sorted(evidence_items, key=lambda item: (item["system"], item["source"]))


def _signal_dict(signal: CanonicalSignal) -> dict[str, Any]:
    return {
        "id": signal.id,
        "domain": signal.domain,
        "polarity": signal.polarity,
        "strength": signal.strength,
        "evidence": [
            {
                "system": ev.system,
                "weight": ev.weight,
                "source": ev.source,
                "value": ev.value,
                "note": ev.note,
            }
            for ev in signal.evidence
        ],
    }


def build_intersection_v2(profile_response: dict[str, Any]) -> dict[str, Any]:
    systems = profile_response.get("systems", {}) if isinstance(profile_response, dict) else {}
    signals = extract_signals_v2(systems)

    grouped: dict[str, list[CanonicalSignal]] = {}
    for signal in signals:
        grouped.setdefault(signal.id, []).append(signal)

    canonical_signals = [_signal_dict(signal) for signal in signals]

    convergences: list[dict[str, Any]] = []
    divergences: list[dict[str, Any]] = []
    bridge_scores: dict[str, float] = {}

    for signal_id, signal_group in sorted(grouped.items(), key=lambda item: item[0]):
        weights = _system_weights(signal_group)
        supporting_systems = [system for system, weight in weights.items() if weight >= 0.4]
        if len(weights) < 2:
            continue

        aggregate_strength = sum(
            _BASELINE_WEIGHTS.get(system, 0.0) * weight for system, weight in weights.items()
        )
        aggregate_strength = min(1.0, round(aggregate_strength, 2))
        confidence = min(
            1.0,
            round(aggregate_strength * (len(supporting_systems) / 4.0) * 1.2, 2),
        )

        strengths = list(weights.values())
        polarity_set = {signal.polarity for signal in signal_group}
        divergent = ("supporting" in polarity_set and "challenging" in polarity_set) or (
            max(strengths) - min(strengths) >= 0.5
        )

        evidence_items = _evidence_list(signal_group)
        systems_list = _ordered_systems(list(weights.keys()))

        if divergent:
            divergences.append(
                {
                    "id": signal_id,
                    "systems": systems_list,
                    "note": "Material divergence across systems.",
                    "evidence": evidence_items,
                }
            )
        elif len(supporting_systems) >= 2:
            convergences.append(
                {
                    "id": signal_id,
                    "systems": _ordered_systems(supporting_systems),
                    "confidence": confidence,
                    "strength": aggregate_strength,
                    "note": "Cross-system support detected.",
                    "evidence": evidence_items,
                }
            )
            bridge_scores[signal_id] = confidence

    convergences.sort(key=lambda item: (-item["confidence"], item["id"]))
    divergences.sort(key=lambda item: (item["id"]))
    bridge_tags = [
        signal_id
        for signal_id, _ in sorted(
            bridge_scores.items(), key=lambda item: (-item[1], item[0])
        )
    ][:5]

    summary_notes = [
        f"Signals: {len(canonical_signals)}.",
        f"Convergences: {len(convergences)}; divergences: {len(divergences)}.",
        f"Bridge tags: {', '.join(bridge_tags) if bridge_tags else 'none'}.",
    ]

    return {
        "meta": {"version": "2.0", "weights": _BASELINE_WEIGHTS, "signalCount": len(canonical_signals)},
        "canonicalSignals": canonical_signals,
        "convergences": convergences,
        "divergences": divergences,
        "bridgeTags": bridge_tags,
        "summary": {"headline": "Intersection v2 summary.", "notes": summary_notes},
    }
