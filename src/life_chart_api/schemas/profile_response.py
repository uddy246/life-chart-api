from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Literal

from pydantic import Field, field_validator, model_validator

from life_chart_api.schemas.core_output import CoreOutput
from life_chart_api.schemas.core_types import (
    DisclaimerBlock,
    Quality,
    StrictBaseModel,
    Subject,
    SystemId,
    SystemUsed,
)
from life_chart_api.schemas.narrative import Narrative
from life_chart_api.schemas.synthesis import Synthesis

ApiVersion = Literal["1.0.0"]
SchemaVersion = Literal["astrology_unified_profile_v1"]


class UnifiedProfileResponse(StrictBaseModel):
    api_version: ApiVersion = Field(default="1.0.0")
    schema_version: SchemaVersion = Field(default="astrology_unified_profile_v1")
    generated_at_utc: datetime
    subject: Subject
    disclaimer_blocks: list[DisclaimerBlock]
    systems_used: list[SystemUsed]
    core_outputs_by_system: Dict[SystemId, CoreOutput]
    synthesis: Synthesis
    narrative: Narrative
    quality: Quality

    @field_validator("generated_at_utc")
    @classmethod
    def _require_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("generated_at_utc must be timezone-aware UTC")
        if v.tzinfo != timezone.utc and v.astimezone(timezone.utc).tzinfo != timezone.utc:
            raise ValueError("generated_at_utc must be UTC")
        return v

    @model_validator(mode="after")
    def _validate_systems(self) -> "UnifiedProfileResponse":
        systems = {entry.system: entry for entry in self.systems_used}
        for required in ("western", "vedic"):
            if required not in systems or not systems[required].enabled:
                raise ValueError("systems_used must include western and vedic enabled entries")
        for required in ("western", "vedic"):
            if required not in self.core_outputs_by_system:
                raise ValueError("core_outputs_by_system must include western and vedic")
        return self
