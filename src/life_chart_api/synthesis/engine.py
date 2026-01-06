from __future__ import annotations

from life_chart_api.schemas.core_output import CoreOutput
from life_chart_api.schemas.core_types import SourceField
from life_chart_api.schemas.synthesis import (
    ActivePhase,
    Confidence,
    ContextualContrast,
    DominantAxis,
    FieldStatus,
    ReinforcedInsight,
    Synthesis,
)


def synthesize(core_by_system: dict[str, CoreOutput]) -> Synthesis:
    field_status = FieldStatus(
        core_identity_theme="compatible",
        motivational_driver="compatible",
        emotional_processing_style="compatible",
        cognitive_decision_style="compatible",
        action_energy_expression="compatible",
        strength_patterns="compatible",
        friction_patterns="compatible",
        relationship_orientation="compatible",
        life_direction_theme="compatible",
        core_lesson_pattern="compatible",
        timing_sensitivity="compatible",
        current_phase_descriptor="system_specific",
        dominant_polarity="compatible",
    )

    reinforced = ReinforcedInsight(
        id="reinforced_1",
        title="Reinforced insight",
        statement="Placeholder reinforced insight statement.",
        sources=[
            SourceField(system="western", field="core_identity_theme"),
            SourceField(system="vedic", field="motivational_driver"),
        ],
        confidence=Confidence(level="medium", reason="Placeholder synthesis rationale."),
    )

    contrast = ContextualContrast(
        id="contrast_1",
        internal_pattern="Placeholder internal pattern.",
        external_demand="Placeholder external demand.",
        explanation="Placeholder contrast explanation.",
        sources=[
            SourceField(system="western", field="friction_patterns"),
        ],
    )

    axis = DominantAxis(
        axis="Autonomy vs duty",
        summary="Placeholder axis summary.",
        sources=[
            SourceField(system="vedic", field="life_direction_theme"),
        ],
    )

    phase = ActivePhase(
        is_present=True,
        phase_descriptor="Placeholder phase descriptor",
        safeguard="This describes a phase, not a permanent state.",
        sources=[
            SourceField(system="western", field="current_phase_descriptor"),
        ],
    )

    return Synthesis(
        method_version="synthesis_v1",
        field_status=field_status,
        reinforced_insights=[reinforced],
        contextual_contrasts=[contrast],
        dominant_axes=[axis],
        active_phase=phase,
    )
