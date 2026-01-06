from __future__ import annotations

from life_chart_api.astrology.western.types import WesternChartFeatures
from life_chart_api.schemas.core_output import CoreOutput

_MOON_STYLE_MAP = {
    "cancer": "internalised",
    "scorpio": "internalised",
    "pisces": "internalised",
    "aries": "externalised",
    "leo": "externalised",
    "sagittarius": "externalised",
    "gemini": "expressive",
    "libra": "expressive",
    "aquarius": "expressive",
    "taurus": "suppressed",
    "virgo": "suppressed",
    "capricorn": "suppressed",
}


def map_western_to_core(f: WesternChartFeatures) -> CoreOutput:
    moon_key = f.moon_sign.strip().lower()
    emotional_style = _MOON_STYLE_MAP.get(moon_key, "cyclical")

    core_identity = f"{f.sun_sign} core with {f.ascendant_sign} presentation"
    action_energy = f.mars_style or "Hesitant-then-committed"
    relationship = f.venus_style or "Independence-preserving"
    lesson = f.saturn_theme or "Responsibility through structure"

    return CoreOutput(
        core_identity_theme=core_identity,
        motivational_driver="Meaning",
        emotional_processing_style=emotional_style,
        cognitive_decision_style="strategic",
        action_energy_expression=action_energy,
        strength_patterns=["Consistency", "Adaptability"],
        friction_patterns=["Overextension"],
        relationship_orientation=relationship,
        life_direction_theme="Purpose with steady refinement",
        core_lesson_pattern=lesson,
        timing_sensitivity="moderately_cyclical",
        current_phase_descriptor="Placeholder phase descriptor",
        dominant_polarity="balanced",
    )
