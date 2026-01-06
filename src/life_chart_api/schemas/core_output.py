from __future__ import annotations

from typing import List

from pydantic import Field, field_validator

from life_chart_api.schemas.core_types import (
    DecisionStyle,
    DominantPolarity,
    EmotionalProcessingStyle,
    StrictBaseModel,
    TimingSensitivity,
)


class CoreOutput(StrictBaseModel):
    core_identity_theme: str
    motivational_driver: str
    emotional_processing_style: EmotionalProcessingStyle
    cognitive_decision_style: DecisionStyle
    action_energy_expression: str
    strength_patterns: List[str]
    friction_patterns: List[str]
    relationship_orientation: str
    life_direction_theme: str
    core_lesson_pattern: str
    timing_sensitivity: TimingSensitivity
    current_phase_descriptor: str | None = None
    dominant_polarity: DominantPolarity

    @field_validator("strength_patterns", "friction_patterns")
    @classmethod
    def _max_three(cls, v: List[str]) -> List[str]:
        if len(v) > 3:
            raise ValueError("max length is 3")
        return v
