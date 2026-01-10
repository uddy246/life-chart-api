from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SourceEvidence(BaseModel):
    system: str
    path: str
    value: Any
    note: str | None = None


class Signal(BaseModel):
    system: str
    theme_id: str
    strength: float
    evidence: SourceEvidence


class IntersectionFinding(BaseModel):
    theme_id: str
    score: float
    systems: list[str]
    evidence: list[SourceEvidence]
    summary: str


class ThemeSummary(BaseModel):
    theme_id: str
    score: float
    systems: list[str]
    evidence: list[SourceEvidence]


class ActionSuggestion(BaseModel):
    theme_id: str
    action: str
    reason: str


class IntersectionReport(BaseModel):
    version: str = "intersection_v1"
    overlaps: list[IntersectionFinding]
    tensions: list[IntersectionFinding]
    dominant_themes: list[ThemeSummary]
    next_actions: list[ActionSuggestion]


_NUMEROLOGY_LIFE_PATH_THEMES: dict[int, str] = {
    1: "initiative",
    2: "harmony",
    3: "expression",
    4: "structure",
    5: "freedom",
    6: "care",
    7: "insight",
    8: "power",
    9: "compassion",
    11: "vision",
    22: "master_builder",
    33: "service",
}
_WESTERN_ELEMENT_THEMES = {
    "fire": "initiative",
    "earth": "structure",
    "air": "intellect",
    "water": "empathy",
}
_WESTERN_MODALITY_THEMES = {
    "cardinal": "leadership",
    "fixed": "stability",
    "mutable": "adaptability",
}
_VEDIC_MOON_SIGN_THEMES = {
    "aries": "initiative",
    "taurus": "stability",
    "cancer": "empathy",
    "virgo": "analysis",
    "libra": "harmony",
    "capricorn": "structure",
}
_VEDIC_NAKSHATRA_THEMES = {
    "ashwini": "initiative",
    "rohini": "abundance",
}
_THEME_LABELS = {
    "initiative": "initiative",
    "harmony": "harmony",
    "expression": "expression",
    "structure": "structure",
    "freedom": "freedom",
    "care": "care",
    "insight": "insight",
    "power": "power",
    "compassion": "compassion",
    "vision": "vision",
    "master_builder": "mastery",
    "service": "service",
    "intellect": "intellect",
    "empathy": "empathy",
    "leadership": "leadership",
    "stability": "stability",
    "adaptability": "adaptability",
    "analysis": "analysis",
    "abundance": "abundance",
}
_CONFLICT_PAIRS = {
    ("initiative", "stability"),
    ("freedom", "structure"),
    ("intellect", "empathy"),
}
_ACTION_MAP = {
    "initiative": ("Choose a clear first step this week.", "Momentum rises with a concrete start."),
    "structure": ("Define one repeatable routine.", "Structure stabilizes progress."),
    "harmony": ("Schedule a check-in with a key relationship.", "Alignment keeps priorities steady."),
    "empathy": ("Create space to reflect before reacting.", "Attunement supports better decisions."),
    "stability": ("Reinforce one boundary or commitment.", "Consistency supports endurance."),
}


def _get_nested(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _sorted_systems(systems: set[str]) -> list[str]:
    return sorted(systems)


def extract_signals(profile: dict[str, Any]) -> list[Signal]:
    systems = profile.get("systems", {}) if isinstance(profile, dict) else {}
    numerology = systems.get("numerology", {}) if isinstance(systems, dict) else {}
    western = systems.get("western", {}) if isinstance(systems, dict) else {}
    vedic = systems.get("vedic", {}) if isinstance(systems, dict) else {}

    signals: list[Signal] = []

    life_path = _get_nested(numerology, ["primitives", "life_path", "reduction", "final_value"])
    if isinstance(life_path, int):
        theme_id = _NUMEROLOGY_LIFE_PATH_THEMES.get(life_path)
        if theme_id:
            signals.append(
                Signal(
                    system="numerology",
                    theme_id=theme_id,
                    strength=0.65,
                    evidence=SourceEvidence(
                        system="numerology",
                        path="systems.numerology.primitives.life_path.reduction.final_value",
                        value=life_path,
                    ),
                )
            )

    elements_high = _get_nested(western, ["strengths", "chartBalance", "elements", "high"])
    if isinstance(elements_high, list):
        for element in elements_high:
            if isinstance(element, str):
                theme_id = _WESTERN_ELEMENT_THEMES.get(element.lower())
                if theme_id:
                    signals.append(
                        Signal(
                            system="western",
                            theme_id=theme_id,
                            strength=0.6,
                            evidence=SourceEvidence(
                                system="western",
                                path="systems.western.strengths.chartBalance.elements.high",
                                value=element,
                            ),
                        )
                    )

    modalities_high = _get_nested(western, ["strengths", "chartBalance", "modalities", "high"])
    if isinstance(modalities_high, list):
        for modality in modalities_high:
            if isinstance(modality, str):
                theme_id = _WESTERN_MODALITY_THEMES.get(modality.lower())
                if theme_id:
                    signals.append(
                        Signal(
                            system="western",
                            theme_id=theme_id,
                            strength=0.58,
                            evidence=SourceEvidence(
                                system="western",
                                path="systems.western.strengths.chartBalance.modalities.high",
                                value=modality,
                            ),
                        )
                    )

    moon_sign = _get_nested(vedic, ["moon_sign"])
    if isinstance(moon_sign, str):
        theme_id = _VEDIC_MOON_SIGN_THEMES.get(moon_sign.lower())
        if theme_id:
            signals.append(
                Signal(
                    system="vedic",
                    theme_id=theme_id,
                    strength=0.6,
                    evidence=SourceEvidence(
                        system="vedic",
                        path="systems.vedic.moon_sign",
                        value=moon_sign,
                    ),
                )
            )

    nakshatra = _get_nested(vedic, ["nakshatra"])
    if isinstance(nakshatra, str):
        theme_id = _VEDIC_NAKSHATRA_THEMES.get(nakshatra.lower())
        if theme_id:
            signals.append(
                Signal(
                    system="vedic",
                    theme_id=theme_id,
                    strength=0.55,
                    evidence=SourceEvidence(
                        system="vedic",
                        path="systems.vedic.nakshatra",
                        value=nakshatra,
                    ),
                )
            )

    return sorted(signals, key=lambda item: (item.theme_id, item.system, item.evidence.path))


def build_intersection_report(signals: list[Signal]) -> IntersectionReport:
    theme_signals: dict[str, list[Signal]] = {}
    for signal in signals:
        theme_signals.setdefault(signal.theme_id, []).append(signal)

    theme_scores: dict[str, float] = {}
    theme_systems: dict[str, list[str]] = {}
    for theme_id, items in theme_signals.items():
        avg_strength = sum(item.strength for item in items) / len(items)
        theme_scores[theme_id] = round(avg_strength, 2)
        theme_systems[theme_id] = _sorted_systems({item.system for item in items})

    overlaps: list[IntersectionFinding] = []
    for theme_id in sorted(theme_signals.keys()):
        systems = theme_systems[theme_id]
        score = theme_scores[theme_id]
        if len(systems) >= 2 and score >= 0.6:
            evidence = [item.evidence for item in theme_signals[theme_id]]
            overlaps.append(
                IntersectionFinding(
                    theme_id=theme_id,
                    score=score,
                    systems=systems,
                    evidence=evidence,
                    summary=f"Overlap on {_THEME_LABELS.get(theme_id, theme_id)}",
                )
            )

    tensions: list[IntersectionFinding] = []
    for left, right in sorted(_CONFLICT_PAIRS):
        left_score = theme_scores.get(left)
        right_score = theme_scores.get(right)
        if left_score is None or right_score is None:
            continue
        if left_score >= 0.55 and right_score >= 0.55:
            systems = _sorted_systems(
                set(theme_systems.get(left, [])) | set(theme_systems.get(right, []))
            )
            if len(systems) >= 2:
                evidence = [item.evidence for item in theme_signals[left] + theme_signals[right]]
                tensions.append(
                    IntersectionFinding(
                        theme_id=f"{left}_vs_{right}",
                        score=round((left_score + right_score) / 2, 2),
                        systems=systems,
                        evidence=evidence,
                        summary=(
                            f"Tension between {_THEME_LABELS.get(left, left)} and "
                            f"{_THEME_LABELS.get(right, right)}"
                        ),
                    )
                )

    dominant_themes: list[ThemeSummary] = []
    for theme_id, score in sorted(
        theme_scores.items(), key=lambda item: (-item[1], item[0])
    )[:3]:
        dominant_themes.append(
            ThemeSummary(
                theme_id=theme_id,
                score=score,
                systems=theme_systems[theme_id],
                evidence=[item.evidence for item in theme_signals[theme_id]],
            )
        )

    next_actions: list[ActionSuggestion] = []
    for theme in dominant_themes:
        action = _ACTION_MAP.get(theme.theme_id)
        if action:
            next_actions.append(
                ActionSuggestion(
                    theme_id=theme.theme_id,
                    action=action[0],
                    reason=action[1],
                )
            )

    return IntersectionReport(
        overlaps=overlaps,
        tensions=tensions,
        dominant_themes=dominant_themes,
        next_actions=next_actions,
    )
