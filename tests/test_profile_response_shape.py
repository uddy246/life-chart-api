from datetime import datetime, timezone

from life_chart_api.schemas.core_output import CoreOutput
from life_chart_api.schemas.core_types import (
    BirthData,
    BirthPlace,
    DisclaimerBlock,
    Quality,
    QualityCompleteness,
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


def test_unified_profile_response_shape():
    core_output = CoreOutput(
        core_identity_theme="Core identity theme",
        motivational_driver="Motivational driver",
        emotional_processing_style="internalised",
        cognitive_decision_style="analytical",
        action_energy_expression="Action energy",
        strength_patterns=["Strength one"],
        friction_patterns=["Friction one"],
        relationship_orientation="Relationship orientation",
        life_direction_theme="Life direction theme",
        core_lesson_pattern="Core lesson pattern",
        timing_sensitivity="relatively_stable",
        current_phase_descriptor=None,
        dominant_polarity="balanced",
    )

    synthesis = Synthesis(
        method_version="1.0",
        field_status=FieldStatus(
            core_identity_theme="reinforced",
            motivational_driver="reinforced",
            emotional_processing_style="reinforced",
            cognitive_decision_style="reinforced",
            action_energy_expression="reinforced",
            strength_patterns="reinforced",
            friction_patterns="reinforced",
            relationship_orientation="reinforced",
            life_direction_theme="reinforced",
            core_lesson_pattern="reinforced",
            timing_sensitivity="reinforced",
            current_phase_descriptor="system_specific",
            dominant_polarity="reinforced",
        ),
        reinforced_insights=[
            ReinforcedInsight(
                id="insight_1",
                title="Insight",
                statement="Insight statement",
                sources=[{"system": "western", "field": "core_identity_theme"}],
                confidence=Confidence(level="high", reason="Consistent across systems"),
            )
        ],
        contextual_contrasts=[
            ContextualContrast(
                id="contrast_1",
                internal_pattern="Internal pattern",
                external_demand="External demand",
                explanation="Explanation",
                sources=[{"system": "vedic", "field": "motivational_driver"}],
            )
        ],
        dominant_axes=[
            DominantAxis(
                axis="Axis",
                summary="Summary",
                sources=[{"system": "western", "field": "life_direction_theme"}],
            )
        ],
        active_phase=ActivePhase(
            is_present=False,
            phase_descriptor="None",
            safeguard="Safeguard",
            sources=[{"system": "western", "field": "current_phase_descriptor"}],
        ),
    )

    narrative = Narrative(
        version="1.0",
        sections=[
            NarrativeSection(
                id="internal_experience",
                title="Internal experience",
                body="Body",
                source_fields=[{"system": "western", "field": "emotional_processing_style"}],
            ),
            NarrativeSection(
                id="external_demands",
                title="External demands",
                body="Body",
                preamble="Preamble",
                source_fields=[{"system": "vedic", "field": "motivational_driver"}],
            ),
            NarrativeSection(
                id="tension",
                title="Tension",
                body="Body",
                source_fields=[{"system": "western", "field": "friction_patterns"}],
            ),
            NarrativeSection(
                id="why_tension_exists",
                title="Why tension exists",
                body="Body",
                source_fields=[{"system": "vedic", "field": "core_lesson_pattern"}],
            ),
            NarrativeSection(
                id="phase",
                title="Phase",
                body="Body",
                safeguard="Safeguard",
                source_fields=[{"system": "western", "field": "current_phase_descriptor"}],
            ),
        ],
    )

    response = UnifiedProfileResponse(
        generated_at_utc=datetime.now(timezone.utc),
        subject=Subject(
            full_name="Test User",
            birth=BirthData(
                date="2000-01-01",
                time="12:00:00",
                place=BirthPlace(name="Test City", lat=0.0, lon=0.0, tz="UTC"),
            ),
        ),
        disclaimer_blocks=[
            DisclaimerBlock(
                id="how_to_read",
                title="How to read this profile",
                body="Body",
            )
        ],
        systems_used=[
            SystemUsed(system="western", version="1.0", enabled=True),
            SystemUsed(system="vedic", version="1.0", enabled=True),
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

    data = response.model_dump()
    ids = [section["id"] for section in data["narrative"]["sections"]]
    assert ids == [
        "internal_experience",
        "external_demands",
        "tension",
        "why_tension_exists",
        "phase",
    ]
