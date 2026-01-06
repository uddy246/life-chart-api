from __future__ import annotations

from typing import List, Literal

from pydantic import Field

from life_chart_api.schemas.core_types import SourceField, StrictBaseModel, SystemId

FieldStatusValue = Literal["reinforced", "compatible", "contradictory", "system_specific"]
ConfidenceLevel = Literal["high", "medium", "low"]


class FieldStatus(StrictBaseModel):
    core_identity_theme: FieldStatusValue
    motivational_driver: FieldStatusValue
    emotional_processing_style: FieldStatusValue
    cognitive_decision_style: FieldStatusValue
    action_energy_expression: FieldStatusValue
    strength_patterns: FieldStatusValue
    friction_patterns: FieldStatusValue
    relationship_orientation: FieldStatusValue
    life_direction_theme: FieldStatusValue
    core_lesson_pattern: FieldStatusValue
    timing_sensitivity: FieldStatusValue
    current_phase_descriptor: FieldStatusValue
    dominant_polarity: FieldStatusValue


class Confidence(StrictBaseModel):
    level: ConfidenceLevel
    reason: str


class ReinforcedInsight(StrictBaseModel):
    id: str
    title: str
    statement: str
    sources: List[SourceField]
    confidence: Confidence


class ContextualContrast(StrictBaseModel):
    id: str
    internal_pattern: str
    external_demand: str
    explanation: str
    sources: List[SourceField]


class DominantAxis(StrictBaseModel):
    axis: str
    summary: str
    sources: List[SourceField]


class ActivePhase(StrictBaseModel):
    is_present: bool
    phase_descriptor: str
    safeguard: str
    sources: List[SourceField]


class Synthesis(StrictBaseModel):
    method_version: str
    field_status: FieldStatus
    reinforced_insights: List[ReinforcedInsight] = Field(default_factory=list)
    contextual_contrasts: List[ContextualContrast] = Field(default_factory=list)
    dominant_axes: List[DominantAxis] = Field(default_factory=list)
    active_phase: ActivePhase
