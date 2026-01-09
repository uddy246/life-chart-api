from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from life_chart_api.synthesis.taxonomy import CANONICAL_TAGS, TAG_KEYWORDS


@dataclass(frozen=True)
class Signal:
    system: str
    tag: str
    polarity: int
    weight: float
    evidence_key: str
    note: str


_NEGATIVE_CUES = ("challenge", "difficult", "tension", "risk", "pressure", "testing")
_POSITIVE_CUES = ("supportive", "strength", "opportunity", "ease", "flow", "growth")


def _collect_text(parts: list[str]) -> str:
    return " ".join(part for part in parts if part).lower()


def _text_from_narrative(narrative: dict[str, Any] | None) -> list[str]:
    if not isinstance(narrative, dict):
        return []
    items: list[str] = []
    headline = narrative.get("headline")
    if isinstance(headline, str):
        items.append(headline)
    sections = narrative.get("sections")
    if isinstance(sections, list):
        for section in sections:
            if isinstance(section, dict):
                for key in ("title", "body"):
                    value = section.get(key)
                    if isinstance(value, str):
                        items.append(value)
                bullets = section.get("bullets")
                if isinstance(bullets, list):
                    items.extend([b for b in bullets if isinstance(b, str)])
    return items


def _text_from_list(items: list[Any] | None) -> list[str]:
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, str)]


def _extract_signals(system: str, blob: str, evidence_key: str) -> list[Signal]:
    signals: list[Signal] = []
    if not blob:
        return signals

    for tag in CANONICAL_TAGS:
        keywords = TAG_KEYWORDS.get(tag, [])
        hits = sum(1 for kw in keywords if kw in blob)
        if hits < 2:
            continue
        weight = min(1.0, hits / 6.0)
        polarity = 1
        if any(cue in blob for cue in _NEGATIVE_CUES):
            polarity = -1
        elif any(cue in blob for cue in _POSITIVE_CUES):
            polarity = 1
        note = f"Tag '{tag}' matched {hits} keywords."
        signals.append(
            Signal(
                system=system,
                tag=tag,
                polarity=polarity,
                weight=weight,
                evidence_key=evidence_key,
                note=note,
            )
        )

    return sorted(signals, key=lambda s: (s.tag, s.system))


def extract_western_signals(western: dict[str, Any]) -> list[Signal]:
    parts: list[str] = []
    parts.extend(_text_from_narrative(western.get("narrative")))
    strengths = western.get("strengths")
    if isinstance(strengths, dict):
        parts.extend(_text_from_list(strengths.get("dominantThemes")))
    career = western.get("career")
    if isinstance(career, dict):
        if isinstance(career.get("nearTermAdvice"), str):
            parts.append(career["nearTermAdvice"])
        vectors = career.get("vectors")
        if isinstance(vectors, list):
            for vector in vectors:
                if isinstance(vector, dict) and isinstance(vector.get("why"), str):
                    parts.append(vector["why"])
    relationships = western.get("relationships")
    if isinstance(relationships, dict):
        style = relationships.get("style")
        if isinstance(style, dict):
            for key in ("bonding", "conflict", "repair"):
                value = style.get(key)
                if isinstance(value, str):
                    parts.append(value)
        notes = relationships.get("notes")
        if isinstance(notes, str):
            parts.append(notes)

    blob = _collect_text(parts)
    return _extract_signals("western", blob, "systems.western.narrative")


def extract_vedic_signals(vedic: dict[str, Any]) -> list[Signal]:
    parts: list[str] = []
    for key in (
        "saturn_theme",
        "life_direction_hint",
        "timing_sensitivity_hint",
        "current_phase_hint",
    ):
        value = vedic.get(key)
        if isinstance(value, str):
            parts.append(value)
    parts.extend(_text_from_list(vedic.get("notes")))
    blob = _collect_text(parts)
    return _extract_signals("vedic", blob, "systems.vedic")


def extract_chinese_signals(chinese: dict[str, Any]) -> list[Signal]:
    parts: list[str] = []
    parts.extend(_text_from_narrative(chinese.get("narrative")))
    elements = chinese.get("elements")
    if isinstance(elements, dict):
        if isinstance(elements.get("balanceAdvice"), str):
            parts.append(elements["balanceAdvice"])
    luck_cycles = chinese.get("luckCycles")
    if isinstance(luck_cycles, dict):
        current = luck_cycles.get("current")
        if isinstance(current, dict):
            for key in ("theme", "advice"):
                value = current.get(key)
                if isinstance(value, str):
                    parts.append(value)
    relationships = chinese.get("relationships")
    if isinstance(relationships, dict):
        if isinstance(relationships.get("style"), str):
            parts.append(relationships["style"])
        if isinstance(relationships.get("notes"), str):
            parts.append(relationships["notes"])
    career = chinese.get("career")
    if isinstance(career, dict):
        if isinstance(career.get("nearTermAdvice"), str):
            parts.append(career["nearTermAdvice"])
        vectors = career.get("vectors")
        if isinstance(vectors, list):
            for vector in vectors:
                if isinstance(vector, dict) and isinstance(vector.get("why"), str):
                    parts.append(vector["why"])

    blob = _collect_text(parts)
    return _extract_signals("chinese", blob, "systems.chinese.narrative")


def extract_numerology_signals(numerology: dict[str, Any] | None) -> list[Signal]:
    if not isinstance(numerology, dict):
        return []
    parts: list[str] = []
    for value in numerology.values():
        if isinstance(value, str):
            parts.append(value)
    blob = _collect_text(parts)
    return _extract_signals("numerology", blob, "systems.numerology")
