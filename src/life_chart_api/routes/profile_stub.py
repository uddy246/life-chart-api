from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from life_chart_api.schemas.core_output import CoreOutput
from life_chart_api.schemas.core_types import (
    BirthData,
    BirthPlace,
    DisclaimerBlock,
    Quality,
    QualityCompleteness,
    SourceField,
    Subject,
    SystemUsed,
)
from life_chart_api.schemas.narrative import Narrative, NarrativeSection
from life_chart_api.schemas.profile_response import UnifiedProfileResponse
from life_chart_api.schemas.synthesis import (
    ActivePhase,
    Confidence,
    ContextualContrast,
    DominantAxis,
    FieldStatus,
    ReinforcedInsight,
    Synthesis,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/stub", response_model=UnifiedProfileResponse)
def get_profile_stub() -> UnifiedProfileResponse:
    now = datetime.now(timezone.utc)

    core_output = CoreOutput(
        core_identity_theme="Placeholder core identity theme",
        motivational_driver="Placeholder motivational driver",
        emotional_processing_style="internalised",
        cognitive_decision_style="analytical",
        action_energy_expression="Placeholder action energy expression",
        strength_patterns=["Strength one", "Strength two"],
        friction_patterns=["Friction one"],
        relationship_orientation="Placeholder relationship orientation",
        life_direction_theme="Placeholder life direction theme",
        core_lesson_pattern="Placeholder core lesson pattern",
        timing_sensitivity="relatively_stable",
        current_phase_descriptor="Placeholder current phase descriptor",
        dominant_polarity="balanced",
    )

    synthesis = Synthesis(
        method_version="synthesis_v1",
        field_status=FieldStatus(
            core_identity_theme="reinforced",
            motivational_driver="compatible",
            emotional_processing_style="reinforced",
            cognitive_decision_style="compatible",
            action_energy_expression="system_specific",
            strength_patterns="reinforced",
            friction_patterns="compatible",
            relationship_orientation="reinforced",
            life_direction_theme="compatible",
            core_lesson_pattern="system_specific",
            timing_sensitivity="reinforced",
            current_phase_descriptor="system_specific",
            dominant_polarity="reinforced",
        ),
        reinforced_insights=[
            ReinforcedInsight(
                id="reinforced_1",
                title="Reinforced insight",
                statement="Placeholder reinforced insight statement.",
                sources=[
                    SourceField(system="western", field="core_identity_theme"),
                    SourceField(system="vedic", field="motivational_driver"),
                ],
                confidence=Confidence(level="high", reason="Placeholder confidence reason."),
            )
        ],
        contextual_contrasts=[
            ContextualContrast(
                id="contrast_1",
                internal_pattern="Placeholder internal pattern.",
                external_demand="Placeholder external demand.",
                explanation="Placeholder contrast explanation.",
                sources=[
                    SourceField(system="western", field="friction_patterns"),
                ],
            )
        ],
        dominant_axes=[
            DominantAxis(
                axis="Placeholder axis",
                summary="Placeholder axis summary.",
                sources=[
                    SourceField(system="vedic", field="life_direction_theme"),
                ],
            )
        ],
        active_phase=ActivePhase(
            is_present=True,
            phase_descriptor="Placeholder phase descriptor",
            safeguard="This describes a phase, not a permanent state.",
            sources=[
                SourceField(system="western", field="current_phase_descriptor"),
            ],
        ),
    )

    narrative = Narrative(
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
                preamble=(
                    "This describes patterns that show up through circumstances, timing, "
                    "and responsibility — not how you define yourself."
                ),
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
                safeguard="This describes a phase, not a permanent state.",
                source_fields=[
                    SourceField(system="western", field="current_phase_descriptor"),
                ],
            ),
        ],
    )

    return UnifiedProfileResponse(
        generated_at_utc=now,
        subject=Subject(
            full_name="Placeholder Name",
            birth=BirthData(
                date="2000-01-01",
                time="12:00:00",
                place=BirthPlace(name="Placeholder City", lat=0.0, lon=0.0, tz="UTC"),
            ),
        ),
        disclaimer_blocks=[
            DisclaimerBlock(
                id="how_to_read",
                title="How to read this profile",
                body="Placeholder disclaimer body.",
            )
        ],
        systems_used=[
            SystemUsed(system="western", version="mapping_v1", enabled=True),
            SystemUsed(system="vedic", version="mapping_v1", enabled=True),
        ],
        core_outputs_by_system={
            "western": core_output,
            "vedic": core_output,
        },
        synthesis=synthesis,
        narrative=narrative,
        quality=Quality(
            completeness=QualityCompleteness(
                western=1.0,
                vedic=1.0,
                synthesis=1.0,
                narrative=1.0,
            ),
            warnings=[],
        ),
    )
