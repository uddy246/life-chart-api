from __future__ import annotations

from life_chart_api.schemas.core_output import CoreOutput
from life_chart_api.schemas.core_types import SourceField
from life_chart_api.schemas.narrative import Narrative, NarrativeSection
from life_chart_api.schemas.synthesis import Synthesis

_EXTERNAL_DEMANDS_PREAMBLE = (
    "This describes patterns that show up through circumstances, timing, and "
    "responsibility — not how you define yourself."
)
_PHASE_SAFEGUARD = "This describes a phase, not a permanent state."


def build_narrative(core_by_system: dict[str, CoreOutput], synthesis: Synthesis) -> Narrative:
    return Narrative(
        version="narrative_v1",
        sections=[
            NarrativeSection(
                id="internal_experience",
                title="Internal experience",
                body="Placeholder internal experience narrative.",
                source_fields=[
                    SourceField(system="western", field="emotional_processing_style"),
                ],
            ),
            NarrativeSection(
                id="external_demands",
                title="External demands",
                body="Placeholder external demands narrative.",
                preamble=_EXTERNAL_DEMANDS_PREAMBLE,
                source_fields=[
                    SourceField(system="vedic", field="action_energy_expression"),
                ],
            ),
            NarrativeSection(
                id="tension",
                title="Tension",
                body="Placeholder tension narrative.",
                source_fields=[
                    SourceField(system="western", field="friction_patterns"),
                ],
            ),
            NarrativeSection(
                id="why_tension_exists",
                title="Why tension exists",
                body="Placeholder explanation of why tension exists.",
                source_fields=[
                    SourceField(system="vedic", field="core_lesson_pattern"),
                ],
            ),
            NarrativeSection(
                id="phase",
                title="Phase",
                body="Placeholder phase narrative.",
                safeguard=_PHASE_SAFEGUARD,
                source_fields=[
                    SourceField(system="western", field="current_phase_descriptor"),
                ],
            ),
        ],
    )
