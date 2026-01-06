from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from life_chart_api.astrology.western.mapper import map_western_to_core
from life_chart_api.astrology.western.types import WesternChartFeatures
from life_chart_api.astrology.vedic.mapper import map_vedic_to_core
from life_chart_api.astrology.vedic.types import VedicChartFeatures
from life_chart_api.narrative.generator import build_narrative
from life_chart_api.schemas.core_types import (
    BirthData,
    BirthPlace,
    DisclaimerBlock,
    Quality,
    QualityCompleteness,
    Subject,
    SystemUsed,
)
from life_chart_api.schemas.profile_response import UnifiedProfileResponse
from life_chart_api.synthesis.engine import synthesize

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileComputeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str
    date: str
    time: str
    place_name: str
    lat: float
    lon: float
    tz: str


@router.post("/compute", response_model=UnifiedProfileResponse)
def compute_profile(payload: ProfileComputeRequest) -> UnifiedProfileResponse:
    now = datetime.now(timezone.utc)

    west_features = WesternChartFeatures(
        sun_sign="Pisces",
        moon_sign="Capricorn",
        ascendant_sign="Gemini",
        dominant_element=None,
        dominant_modality=None,
        mercury_style="Pragmatic",
        mars_style="Hesitant-then-committed",
        venus_style="Independence-preserving",
        saturn_theme="Responsibility through structure",
        notes=[],
    )

    core_west = map_western_to_core(west_features)
    vedic_features = VedicChartFeatures(
        lagna_sign="Capricorn",
        lagna_lord="Saturn",
        moon_sign="Taurus",
        moon_afflicted=False,
        saturn_theme="Responsibility through structure",
        rahu_ketu_emphasis=False,
        life_direction_hint="Gradual ascent through responsibility",
        timing_sensitivity_hint="high",
        current_phase_hint="Disciplined consolidation phase",
        notes=[],
    )
    core_vedic = map_vedic_to_core(vedic_features)

    core_by_system = {"western": core_west, "vedic": core_vedic}
    synth = synthesize(core_by_system)
    narr = build_narrative(core_by_system, synth)

    return UnifiedProfileResponse(
        generated_at_utc=now,
        subject=Subject(
            full_name=payload.full_name,
            birth=BirthData(
                date=payload.date,
                time=payload.time,
                place=BirthPlace(
                    name=payload.place_name,
                    lat=payload.lat,
                    lon=payload.lon,
                    tz=payload.tz,
                ),
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
        core_outputs_by_system=core_by_system,
        synthesis=synth,
        narrative=narr,
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
