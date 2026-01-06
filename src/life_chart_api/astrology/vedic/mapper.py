from __future__ import annotations

from life_chart_api.astrology.vedic.types import VedicChartFeatures
from life_chart_api.schemas.core_output import CoreOutput

_TIMING_HINT_MAP = {
    "high": "highly_time_sensitive",
    "medium": "moderately_cyclical",
    "low": "relatively_stable",
}


def map_vedic_to_core(f: VedicChartFeatures) -> CoreOutput:
    identity_parts = [f.lagna_sign]
    if f.saturn_theme:
        identity_parts.append(f.saturn_theme)
    core_identity = " | ".join(identity_parts)

    emotional_style = "suppressed" if f.moon_afflicted else "cyclical"
    timing_sensitivity = _TIMING_HINT_MAP.get(
        (f.timing_sensitivity_hint or "").strip().lower(),
        "highly_time_sensitive",
    )

    life_direction = f.life_direction_hint or "Gradual ascent through responsibility"
    lesson = f.saturn_theme or "Patience under unequal effort-reward cycles"
    phase = f.current_phase_hint or "Placeholder Vedic phase descriptor"

    return CoreOutput(
        core_identity_theme=core_identity,
        motivational_driver="Responsibility",
        emotional_processing_style=emotional_style,
        cognitive_decision_style="deliberate",
        action_energy_expression="Disciplined effort with delayed payoff",
        strength_patterns=["Endurance", "Consistency"],
        friction_patterns=["Overextension"],
        relationship_orientation="Duty-based commitment",
        life_direction_theme=life_direction,
        core_lesson_pattern=lesson,
        timing_sensitivity=timing_sensitivity,
        current_phase_descriptor=phase,
        dominant_polarity="balanced",
    )
